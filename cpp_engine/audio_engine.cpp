#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <mmsystem.h>
#include <iostream>
#include <cstring>
#include <chrono>
#include <thread>
#include <string>

#pragma comment(lib, "winmm.lib")
#pragma comment(lib, "user32.lib")

class AudioEngine {
private:
    HWAVEIN waveIn;
    WAVEHDR waveHeader;
    char audioBuffer[4096];
    bool isCapturing;
    bool noiseCancellationEnabled;
    int noiseThreshold;
    double latency;
    std::chrono::steady_clock::time_point lastCapture;
    bool isInitialized;
    int currentLevel;
    
public:
    AudioEngine() : isCapturing(false), noiseCancellationEnabled(true), 
                    noiseThreshold(30), latency(0.0), isInitialized(false), 
                    currentLevel(0) {
        memset(audioBuffer, 0, sizeof(audioBuffer));
        memset(&waveHeader, 0, sizeof(waveHeader));
    }
    
    bool init(const char* deviceName) {
        if (isInitialized) return true;
        
        WAVEFORMATEX waveFormat;
        waveFormat.wFormatTag = WAVE_FORMAT_PCM;
        waveFormat.nChannels = 1;
        waveFormat.nSamplesPerSec = 8000;  // Lower for faster
        waveFormat.nAvgBytesPerSec = 8000 * 1 * 2;
        waveFormat.nBlockAlign = 2;
        waveFormat.wBitsPerSample = 16;
        waveFormat.cbSize = 0;
        
        MMRESULT result = waveInOpen(&waveIn, WAVE_MAPPER, &waveFormat, 
                                     0, 0, CALLBACK_NULL);
        
        if (result != MMSYSERR_NOERROR) {
            return false;
        }
        
        waveHeader.lpData = audioBuffer;
        waveHeader.dwBufferLength = sizeof(audioBuffer);
        waveHeader.dwBytesRecorded = 0;
        waveHeader.dwUser = 0;
        waveHeader.dwFlags = 0;
        waveHeader.dwLoops = 1;
        
        waveInPrepareHeader(waveIn, &waveHeader, sizeof(WAVEHDR));
        
        isInitialized = true;
        return true;
    }
    
    void startCapture() {
        if (!isInitialized || isCapturing) return;
        
        waveInAddBuffer(waveIn, &waveHeader, sizeof(WAVEHDR));
        waveInStart(waveIn);
        isCapturing = true;
        lastCapture = std::chrono::steady_clock::now();
    }
    
    void stopCapture() {
        if (!isCapturing) return;
        
        waveInStop(waveIn);
        waveInReset(waveIn);
        isCapturing = false;
    }
    
    int getAudioLevel() {
        if (!isCapturing) return 0;
        
        // Check if data is ready
        if (!(waveHeader.dwFlags & WHDR_DONE)) {
            return currentLevel;
        }
        
        // Calculate latency
        auto now = std::chrono::steady_clock::now();
        latency = std::chrono::duration<double, std::milli>(now - lastCapture).count();
        lastCapture = now;
        
        // Calculate audio level
        int maxLevel = 0;
        int len = waveHeader.dwBytesRecorded;
        
        if (len > 0) {
            short* samples = (short*)audioBuffer;
            int sampleCount = len / 2;
            
            for (int i = 0; i < sampleCount && i < 100; i++) {
                int absSample = abs(samples[i]);
                if (absSample > maxLevel) {
                    maxLevel = absSample;
                }
            }
        }
        
        // Apply noise gate
        if (noiseCancellationEnabled && maxLevel < noiseThreshold) {
            maxLevel = 0;
        }
        
        currentLevel = maxLevel;
        
        // Prepare next buffer
        waveHeader.dwBytesRecorded = 0;
        waveHeader.dwFlags = 0;
        waveInAddBuffer(waveIn, &waveHeader, sizeof(WAVEHDR));
        
        return currentLevel;
    }
    
    double getLatency() {
        return latency;
    }
    
    void setNoiseThreshold(int threshold) {
        noiseThreshold = threshold;
    }
    
    void enableNoiseCancellation(bool enable) {
        noiseCancellationEnabled = enable;
    }
    
    bool isActive() {
        return isCapturing;
    }
    
    void cleanup() {
        if (isCapturing) stopCapture();
        if (isInitialized) {
            waveInUnprepareHeader(waveIn, &waveHeader, sizeof(WAVEHDR));
            waveInClose(waveIn);
            isInitialized = false;
        }
    }
};

static AudioEngine* g_engine = nullptr;

extern "C" {
    
    __declspec(dllexport) bool init_audio_engine(const char* device_name) {
        if (g_engine) {
            delete g_engine;
            g_engine = nullptr;
        }
        g_engine = new AudioEngine();
        return g_engine->init(device_name);
    }
    
    __declspec(dllexport) void start_capture() {
        if (g_engine) g_engine->startCapture();
    }
    
    __declspec(dllexport) void stop_capture() {
        if (g_engine) g_engine->stopCapture();
    }
    
    __declspec(dllexport) const char* get_latest_audio() {
        return nullptr;  // Not used
    }
    
    __declspec(dllexport) void free_audio_buffer() {
        // Not used
    }
    
    __declspec(dllexport) void enable_noise_cancellation(bool enable) {
        if (g_engine) g_engine->enableNoiseCancellation(enable);
    }
    
    __declspec(dllexport) void set_noise_threshold(int threshold) {
        if (g_engine) g_engine->setNoiseThreshold(threshold);
    }
    
    __declspec(dllexport) bool detect_wake_word(const char* audio_data) {
        return false;  // Not used
    }
    
    __declspec(dllexport) double get_audio_latency() {
        if (g_engine) return g_engine->getLatency();
        return 0.0;
    }
    
    __declspec(dllexport) int get_audio_level() {
        if (g_engine) return g_engine->getAudioLevel();
        return 0;
    }
    
    __declspec(dllexport) bool is_audio_active() {
        if (g_engine) return g_engine->isActive();
        return false;
    }
    
    __declspec(dllexport) void cleanup_audio_engine() {
        if (g_engine) {
            g_engine->cleanup();
            delete g_engine;
            g_engine = nullptr;
        }
    }
}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    return TRUE;
}