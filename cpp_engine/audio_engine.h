#ifndef AUDIO_ENGINE_H
#define AUDIO_ENGINE_H

#ifdef _WIN32
    #ifdef AUDIO_EXPORTS
        #define AUDIO_API __declspec(dllexport)
    #else
        #define AUDIO_API __declspec(dllimport)
    #endif
#else
    #define AUDIO_API
#endif

#include <string>
#include <vector>

extern "C" {
    // Core functions
    AUDIO_API bool init_audio_engine(const char* device_name);
    AUDIO_API void start_capture();
    AUDIO_API void stop_capture();
    AUDIO_API const char* get_latest_audio();
    AUDIO_API void free_audio_buffer();
    
    // Noise cancellation
    AUDIO_API void enable_noise_cancellation(bool enable);
    AUDIO_API void set_noise_threshold(int threshold);
    
    // Wake word detection
    AUDIO_API bool detect_wake_word(const char* audio_data);
    AUDIO_API void set_wake_word(const char* word);
    
    // Performance
    AUDIO_API double get_audio_latency();
    AUDIO_API int get_audio_level();
    
    // Cleanup
    AUDIO_API void cleanup_audio_engine();
}

#endif