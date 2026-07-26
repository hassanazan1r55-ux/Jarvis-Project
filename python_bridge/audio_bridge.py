import os
import sys
import ctypes
import time
import threading
from pathlib import Path

# ============================================
# DLL PATH CONFIGURATION
# ============================================

mingw_paths = [
    r"C:\mingw32\bin",
    r"C:\mingw64\bin",
    r"C:\MinGW\bin",
    r"C:\Program Files\mingw-w64\bin",
]

for path in mingw_paths:
    if os.path.exists(path):
        try:
            os.add_dll_directory(path)
        except:
            pass

current_dir = os.path.dirname(os.path.abspath(__file__))
os.add_dll_directory(current_dir)

project_root = os.path.abspath(os.path.join(current_dir, ".."))
cpp_engine_dir = os.path.join(project_root, "cpp_engine")

if os.path.exists(cpp_engine_dir):
    os.add_dll_directory(cpp_engine_dir)

os.add_dll_directory(os.getcwd())

# ============================================
# CPP AUDIO ENGINE CLASS (FAST)
# ============================================

class CppAudioEngine:
    """Python bridge to C++ audio engine DLL - FAST"""
    
    def __init__(self, dll_path=None):
        self.dll_path = dll_path or self._find_dll()
        self.dll = None
        self.is_initialized = False
        self._last_audio = ""
        self._load_dll()
    
    def _find_dll(self):
        """Find audio_engine.dll"""
        possible_paths = [
            os.path.join(cpp_engine_dir, "audio_engine.dll"),
            os.path.join(project_root, "audio_engine.dll"),
            os.path.join(os.getcwd(), "audio_engine.dll"),
            os.path.join(os.getcwd(), "cpp_engine", "audio_engine.dll"),
            os.path.join(current_dir, "audio_engine.dll"),
            "audio_engine.dll",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        raise FileNotFoundError("audio_engine.dll not found!")
    
    def _load_dll(self):
        """Load C++ DLL"""
        try:
            print(f"📂 Loading DLL: {self.dll_path}")
            self.dll = ctypes.CDLL(self.dll_path)
            self._setup_functions()
            print("✅ C++ DLL Loaded Successfully! 🚀")
            return True
        except Exception as e:
            print(f"❌ DLL Load Error: {e}")
            raise
    
    def _setup_functions(self):
        """Setup function signatures"""
        self.dll.init_audio_engine.argtypes = [ctypes.c_char_p]
        self.dll.init_audio_engine.restype = ctypes.c_bool
        
        self.dll.start_capture.argtypes = []
        self.dll.start_capture.restype = None
        
        self.dll.stop_capture.argtypes = []
        self.dll.stop_capture.restype = None
        
        self.dll.get_latest_audio.argtypes = []
        self.dll.get_latest_audio.restype = ctypes.c_char_p
        
        self.dll.get_audio_latency.argtypes = []
        self.dll.get_audio_latency.restype = ctypes.c_double
        
        self.dll.get_audio_level.argtypes = []
        self.dll.get_audio_level.restype = ctypes.c_int
        
        self.dll.enable_noise_cancellation.argtypes = [ctypes.c_bool]
        self.dll.enable_noise_cancellation.restype = None
        
        self.dll.is_audio_active.argtypes = []
        self.dll.is_audio_active.restype = ctypes.c_bool
        
        self.dll.cleanup_audio_engine.argtypes = []
        self.dll.cleanup_audio_engine.restype = None
        
        self.dll.set_noise_threshold.argtypes = [ctypes.c_int]
        self.dll.set_noise_threshold.restype = None
    
    def init(self, device_name=None):
        """Initialize audio engine"""
        try:
            if device_name:
                result = self.dll.init_audio_engine(device_name.encode('utf-8'))
            else:
                result = self.dll.init_audio_engine(None)
            
            self.is_initialized = result
            
            # Set noise threshold for better detection
            if result:
                self.dll.set_noise_threshold(50)  # Lower threshold = more sensitive
                
            return result
        except Exception as e:
            print(f"❌ Init error: {e}")
            return False
    
    def start(self):
        """Start audio capture"""
        if not self.is_initialized:
            raise RuntimeError("Engine not initialized!")
        self.dll.start_capture()
    
    def stop(self):
        """Stop audio capture"""
        self.dll.stop_capture()
    
    def get_audio(self):
        """Get latest audio data - FAST"""
        if not self.is_initialized:
            return None
        
        try:
            audio_ptr = self.dll.get_latest_audio()
            if audio_ptr:
                # Convert bytes to string
                audio_str = audio_ptr.decode('utf-8', errors='ignore')
                if audio_str:
                    self._last_audio = audio_str
                    return audio_str
            return self._last_audio
        except:
            return None
    
    def get_latency(self):
        """Get audio latency in milliseconds"""
        try:
            return self.dll.get_audio_latency()
        except:
            return 0.0
    
    def get_level(self):
        """Get audio level"""
        try:
            return self.dll.get_audio_level()
        except:
            return 0
    
    def set_noise_cancellation(self, enable):
        """Enable/disable noise cancellation"""
        try:
            self.dll.enable_noise_cancellation(enable)
        except:
            pass
    
    def set_noise_threshold(self, threshold):
        """Set noise threshold (lower = more sensitive)"""
        try:
            self.dll.set_noise_threshold(threshold)
        except:
            pass
    
    def is_active(self):
        """Check if capturing"""
        try:
            return self.dll.is_audio_active()
        except:
            return False
    
    def cleanup(self):
        """Cleanup resources"""
        if self.dll:
            try:
                self.dll.cleanup_audio_engine()
            except:
                pass
            self.is_initialized = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


# ============================================
# TEST FUNCTION
# ============================================

def test_engine():
    """Test the C++ audio engine"""
    print("="*50)
    print("🧪 Testing C++ Audio Engine (FAST)")
    print("="*50)
    
    try:
        with CppAudioEngine() as engine:
            print("\n🔧 Initializing...")
            if engine.init():
                print("✅ Engine ready!")
                
                # Optimize settings
                engine.set_noise_cancellation(True)
                engine.set_noise_threshold(30)  # More sensitive
                
                # Start capture
                engine.start()
                print("🎤 Listening for 3 seconds...")
                print("📊 Audio levels (higher = louder):")
                
                # Get initial latency
                time.sleep(0.5)
                
                for i in range(30):
                    audio = engine.get_audio()
                    level = engine.get_level()
                    latency = engine.get_latency()
                    
                    # Status
                    if level > 500:
                        status = "🔊 LOUD"
                    elif level > 50:
                        status = "🔉 medium"
                    else:
                        status = "🔇 silent"
                    
                    print(f"  [{i+1:2d}] Level: {level:5d} | {status:8s} | Latency: {latency:5.2f}ms", end="\r")
                    
                    # If level is high, show audio preview
                    if level > 100 and audio:
                        preview = audio[:30] if len(audio) > 30 else audio
                        print(f"\n  📝 Audio: {preview}...")
                    
                    time.sleep(0.1)
                
                print("\n")
                
                # Stop
                engine.stop()
                
                print("\n📊 Final Statistics:")
                print(f"  ✅ Last latency: {engine.get_latency():.2f}ms")
                print(f"  ✅ Last level: {engine.get_level()}")
                
                print("\n✅ Test complete!")
                return True
                
            else:
                print("❌ Failed to initialize engine!")
                return False
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_engine()
    if success:
        print("\n🎉 C++ Audio Engine is working!")
        print("⚡ Latency should be < 50ms for best performance")
    else:
        print("\n⚠️ Test failed!")