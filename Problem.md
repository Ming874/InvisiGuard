# Problem Statement

In the digital age, protecting intellectual property and verifying the authenticity of digital images is a significant challenge. Unauthorized use, distribution, and modification of images are widespread. Traditional watermarking techniques are often either too visible, degrading the image quality, or too fragile, failing to survive common image manipulations like compression, noise, and cropping.

There is a need for a robust and invisible watermarking system that can:

1.  **Embed information invisibly**: The watermark should not be perceptible to the human eye, maintaining the original image's quality.
2.  **Survive common manipulations**: The watermark must be resilient to typical image processing operations, such as lossless compression, brightness adjustments, and minor cropping.
3.  **Provide reliable verification**: It should be possible to accurately extract the embedded information to verify ownership and authenticity, both with and without the original image.

InvisiGuard addresses this problem by implementing a sophisticated watermarking scheme based on Discrete Wavelet Transform (DWT), Quantization Index Modulation (QIM), and Reed-Solomon error correction to provide a robust, high-fidelity, and secure invisible watermarking solution.
