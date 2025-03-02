import wave
import io
import simpleaudio as sa

global play_obj # GC による削除を防ぐ
play_obj = None

class WaveHandler:
    def write(self, filename, wavedata):
        with open(filename, 'wb') as f:
            f.write(wavedata)

    def read(self, filename):
        with open(filename, 'rb') as f:
            wavedata = f.read()
            return wavedata

    def get_wavedata_info(self, wavedata):
        with wave.open(io.BytesIO(wavedata), "rb") as wf:
            # WAVファイルのパラメータを取得
            num_channels = wf.getnchannels()  # チャンネル数（モノラルorステレオ）
            sample_width = wf.getsampwidth()  # サンプル幅（バイト数）
            frame_rate = wf.getframerate()    # サンプリングレート
            num_frames = wf.getnframes()      # フレーム数
            # 音声データを読み込む
            audio_data = wf.readframes(num_frames)
            params = wf.getparams()

        return num_channels, sample_width, frame_rate, num_frames, audio_data            

    def play(self, wavedata):
    	# 再生終了するまで待つようにしたいが、その方法がわからないので後回し。
        num_channels, sample_width, frame_rate, _, audio_data = self.get_wavedata_info(wavedata)           

        # 読み込んだデータを再生
        play_obj = sa.play_buffer(audio_data, num_channels, sample_width, frame_rate)

        # 再生終了を待つ
        # play_obj.wait_done()

        # ループで終了を待機するバージョン
        import time
        while play_obj.is_playing():
            time.sleep(0.1)
    
    def get_length(self, wavedata):
        _, _, frame_rate, num_frames, _ = self.get_wavedata_info(wavedata)           
        duration_sec = num_frames / frame_rate
        return duration_sec

    def show_wavedata_info(self, wavedata):
        num_channels, sample_width, frame_rate, num_frames, _ = self.get_wavedata_info(wavedata)           
        print(f"チャンネル数: {num_channels}")
        print(f"サンプル幅: {sample_width} byte")
        print(f"サンプリングレート: {frame_rate} Hz")
        print(f"フレーム数: {num_frames} フレーム")
        print(f"再生時間: {num_frames / frame_rate} 秒")

    def show_wavefile_info(self, filename):
        print(f"ファイル名: {filename}")
        wavedata = self.read(filename)
        self.show_wavedata_info(wavedata)

if __name__ == "__main__":
    INPUT_WAVE_FILE = 'testdata/whtest00.wav'
    OUTPUT_WAVE_FILE = 'testdata/result.wav'
    wh = WaveHandler()
    wavedata = wh.read(INPUT_WAVE_FILE)
    wh.show_wavedata_info(wavedata)
    print(wh.get_length(wavedata))

    wh.write(OUTPUT_WAVE_FILE, wavedata)
    wavedata = wh.read(OUTPUT_WAVE_FILE)
    wh.show_wavedata_info(wavedata)
    print(wh.get_length(wavedata))
    
    print('done')

