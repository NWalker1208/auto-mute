// https://gist.github.com/tatsuyasusukida/b6daa0cd09bba2fbbf6289c58777eeca
class AudioRecorder extends AudioWorkletProcessor {
  process(inputs, outputs, parameters) {
    const buffer = []
    const channel = 0

    for (let t = 0; t < inputs[0][channel].length; t += 1) {
      buffer.push(inputs[0][channel][t]);
    }

    if (buffer.length >= 1) {
      this.port.postMessage({buffer})
    }

    return true;
  }
}

registerProcessor('auto-recorder', AudioRecorder);
