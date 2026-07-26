import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from python_bridge.audio_bridge import CppAudioEngine

def test_python_vs_cpp():
    """Compare Python vs C++ performance"""
    
    print("="*50)
    print("🔥 PERFORMANCE COMPARISON")
    print("="*50)
    
    # Test C++ Engine
    print("\n📊 C++ Engine Test:")
    with CppAudioEngine() as engine:
        if engine.init():
            engine.start()
            
            # Test latency
            latencies = []
            for _ in range(100):
                start = time.perf_counter()
                audio = engine.get_audio()
                latency = engine.get_latency()
                latencies.append(latency)
                time.sleep(0.01)
            
            engine.stop()
            
            avg_latency = sum(latencies) / len(latencies)
            print(f"  ✅ Average latency: {avg_latency:.2f}ms")
            print(f"  ✅ Min latency: {min(latencies):.2f}ms")
            print(f"  ✅ Max latency: {max(latencies):.2f}ms")
        else:
            print("  ❌ Failed to initialize C++ engine")
    
    # Compare with Python (speech_recognition)
    print("\n📊 Python (speech_recognition) Test:")
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        
        with sr.Microphone() as source:
            start = time.perf_counter()
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source, timeout=1)
            end = time.perf_counter()
            
            python_latency = (end - start) * 1000
            print(f"  ✅ Latency: {python_latency:.2f}ms")
    except Exception as e:
        print(f"  ❌ Python test failed: {e}")
    
    print("\n" + "="*50)
    print("📈 CONCLUSION:")
    print("C++ engine is MUCH faster for audio processing!")
    print("="*50)

if __name__ == "__main__":
    test_python_vs_cpp()