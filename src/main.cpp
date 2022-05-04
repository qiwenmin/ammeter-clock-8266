#include <Arduino.h>
#include <ArduinoOTA.h>
#include <Ticker.h>
#include <WiFiUdp.h>
#include <NTPClient.h>

// hardware
#define STATE_LED_PIN (2)
#define HOUR_LED_PIN (13)
#define MINUTE_LED_PIN (12)

#define OUTPUT_PIN (14)

#define BTN_PIN (16)

#define HOSTNAME_PREFIX "amclock-"

// WiFi
static WiFiEventHandler wifi_connected_handler;
static WiFiEventHandler wifi_disconnected_handler;

// State LED
static const uint16_t state_pattern_normal = 0b0000111100001111;
static const uint16_t state_pattern_connecting = 0b1100110000000000;
static const uint16_t state_pattern_smartconfig = 0b1111111100000000;

static uint16_t state_pattern = state_pattern_normal;

static Ticker state_led_ticker;

// PWM output
static int output_val = 0;
static Ticker output_ticker;
static const int output_smooth_step = 32;
static const uint32_t output_smooth_interval_ms = 32;

// NTP
static WiFiUDP ntp_udp;
static NTPClient time_client(ntp_udp, "pool.ntp.org");
static const int time_offset = 3600 * 8;

void setup() {
    // Init Push button
    pinMode(BTN_PIN, INPUT_PULLUP);

    // Init state led
    pinMode(STATE_LED_PIN, OUTPUT);
    digitalWrite(STATE_LED_PIN, LOW);

    state_led_ticker.attach_ms(125, []() {
        digitalWrite(STATE_LED_PIN, !(state_pattern & 0x01));
        state_pattern = (state_pattern >> 1) | (state_pattern << 15);
    });

    // Init time leds
    pinMode(HOUR_LED_PIN, OUTPUT);
    digitalWrite(HOUR_LED_PIN, LOW);

    pinMode(MINUTE_LED_PIN, OUTPUT);
    digitalWrite(MINUTE_LED_PIN, LOW);

    // Init PWM output
    analogWriteRange(1023);
    analogWrite(OUTPUT_PIN, 0);

    // Init WiFi
    WiFi.mode(WIFI_STA);

    // Is the button pressed?
    if (digitalRead(BTN_PIN) == LOW) {
        // smart config...
        state_pattern = state_pattern_smartconfig;

        WiFi.beginSmartConfig();

        while (1) {
            if (WiFi.smartConfigDone()) {
                WiFi.setAutoConnect(true);
                break;
            }

            delay(25);
        }
    }

    state_pattern = state_pattern_connecting;
    auto chipIdHex = String(ESP.getChipId(), HEX);
    String hostname = HOSTNAME_PREFIX + chipIdHex;
    WiFi.setHostname(hostname.c_str());

    wifi_connected_handler = WiFi.onStationModeGotIP([](const WiFiEventStationModeGotIP &) {
        state_pattern = state_pattern_normal;
    });

    wifi_disconnected_handler = WiFi.onStationModeDisconnected([](const WiFiEventStationModeDisconnected &) {
        state_pattern = state_pattern_connecting;
    });

    WiFi.begin();

    // Init OTA
    ArduinoOTA.setHostname(hostname.c_str());
    ArduinoOTA.begin();

    // Init output ticker
    output_ticker.attach_ms(output_smooth_interval_ms, []() {
        static int cur_output_val = 0;

        if (cur_output_val < output_val) {
            cur_output_val += output_smooth_step;
            if (cur_output_val > output_val) cur_output_val = output_val;
            analogWrite(OUTPUT_PIN, cur_output_val);
        } else if (cur_output_val > output_val) {
            cur_output_val -= output_smooth_step;
            if (cur_output_val < output_val) cur_output_val = output_val;
            analogWrite(OUTPUT_PIN, cur_output_val);
        }
    });

    // Init ntp client
    time_client.begin();
    time_client.setTimeOffset(time_offset);
}

void loop() {
    ArduinoOTA.handle();

    static auto time_update_at = millis();
    if ((millis() - time_update_at) >= 1000) {
        if (digitalRead(BTN_PIN) == LOW) {
            // calibrate
            digitalWrite(HOUR_LED_PIN, HIGH);
            digitalWrite(MINUTE_LED_PIN, HIGH);
            output_val = 1023;
        } else {
            time_update_at = millis();
            time_client.update();
            if (time_client.isTimeSet()) {
                int h = time_client.getHours();
                int m = time_client.getMinutes();
                int s = time_client.getSeconds();

                h = h % 12;

                if ((s / 10) & 0x01) {
                    // 1x, 3x, 5x seconds
                    int v = m * 1023 / 60;

                    output_val = v;
                    digitalWrite(HOUR_LED_PIN, LOW);
                    digitalWrite(MINUTE_LED_PIN, !digitalRead(MINUTE_LED_PIN));
                } else {
                    // 0x, 2x, 4x seconds
                    int seconds = h * 3600 + m * 60 + s;
                    int v = seconds * 1023 / 12 / 3600;

                    output_val = v;
                    digitalWrite(HOUR_LED_PIN, HIGH);
                    digitalWrite(MINUTE_LED_PIN, LOW);
                }
            }
        }
    }
}
