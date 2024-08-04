import { pipeline, env } from '@xenova/transformers'

env.allowLocalModels = false;

const transcriber = await pipeline(
  "automatic-speech-recognition",
  "Xenova/whisper-tiny.en",
  {
    quantized: true
  }
);

export async function transcribe(audioData: AudioBuffer) {
  let audio = audioData.getChannelData(0);
  
  let output = await transcriber(audio, {
    task: "transcribe",
    return_timestamps: true,
  });

  console.log(output);
}

// https://stackoverflow.com/a/72252279
function _getMicrophoneUserMedia() {
  return navigator.mediaDevices.getUserMedia({
    video: false,
    audio: {
      echoCancellation: true,
      noiseSuppression: true,
    },
  })
}

// TODO: see https://github.com/xenova/whisper-web/blob/main/src/components/AudioRecorder.tsx instead
//       https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder
//       https://github.com/xenova/whisper-web/blob/81869ed62970ff4373509b6004a6c9a3f0c5b64d/src/components/AudioManager.tsx#L173

// https://gist.github.com/tatsuyasusukida/b6daa0cd09bba2fbbf6289c58777eeca
export async function recordAudio(audioContext: AudioContext) {
  const mediaStream = await _getMicrophoneUserMedia();

  await audioContext.audioWorklet.addModule('audio-recorder.js')
  const mediaStreamSource = audioContext.createMediaStreamSource(mediaStream);
  const audioRecorder = new AudioWorkletNode(audioContext, 'audio-recorder');
  const buffers = []

  audioRecorder.port.addEventListener('message', event => {
    buffers.push(event.data.buffer);
    console.log(event.data.buffer);
  });
  audioRecorder.port.start();

  mediaStreamSource.connect(audioRecorder);
  audioRecorder.connect(audioContext.destination);
}

const startButton = document.querySelector<HTMLButtonElement>('#start')!;
startButton.addEventListener('click', event => {
  recordAudio(new AudioContext());
});
