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

    def play(self, wavedata):
        with wave.open(io.BytesIO(wavedata), "rb") as wf:
            # WAVファイルのパラメータを取得
            num_channels = wf.getnchannels()  # チャンネル数（モノラルorステレオ）
            sample_width = wf.getsampwidth()  # サンプル幅（バイト数）
            frame_rate = wf.getframerate()    # サンプリングレート
            num_frames = wf.getnframes()      # フレーム数

            # 音声データを読み込む
            audio_data = wf.readframes(num_frames)

        # 読み込んだデータを再生
        play_obj = sa.play_buffer(audio_data, num_channels, sample_width, frame_rate)

        # 再生終了を待つ
        play_obj.wait_done()
        # import time
        # while play_obj.is_playing():
        #     time.sleep(0.1)  # 少し待機しながらループ
        # print('done')

    def get_length(self, wavedata):
        with wave.open(io.BytesIO(wavedata), "rb") as wav_file:
            frame_rate = wav_file.getframerate()
            num_frames = wav_file.getnframes()
            duration_sec = num_frames / frame_rate
        return duration_sec

if __name__ == "__main__":
    wh = WaveHandler()
    wavedata = wh.read('rap.wav')
    print(wh.get_length(wavedata))
    wh.play(wavedata)
    print('done')
    wh.write('test2.wav', wavedata)
    wh.play(wavedata)
    print('done')

