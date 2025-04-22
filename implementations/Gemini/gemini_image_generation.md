# Generate Images

The Gemini API supports image generation using Imagen 3. This guide helps you get started with the model.

## Before You Begin

Before calling the Gemini API, ensure you have your SDK of choice installed, and a Gemini API key configured and ready to use.

## Generate Images Using Imagen 3

The Gemini API provides access to Imagen 3, Google's highest quality text-to-image model, featuring a number of new and improved capabilities. Imagen 3 can do the following:

- Generate images with better detail, richer lighting, and fewer distracting artifacts than previous models
- Understand prompts written in natural language
- Generate images in a wide range of formats and styles
- Render text more effectively than previous models

> **Note**: Imagen 3 is only available on the Paid Tier and always includes a SynthID watermark.

```python
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

client = genai.Client(api_key='GEMINI_API_KEY')

response = client.models.generate_images(
    model='imagen-3.0-generate-002',
    prompt='Robot holding a red skateboard',
    config=types.GenerateImagesConfig(
        number_of_images= 4,
    )
)
for generated_image in response.generated_images:
  image = Image.open(BytesIO(generated_image.image.image_bytes))
  image.show()
```

### Imagen Model Parameters
(Naming conventions vary by programming language.)

- **numberOfImages**: The number of images to generate, from 1 to 4 (inclusive). The default is 4.
- **aspectRatio**: Changes the aspect ratio of the generated image. Supported values are "1:1", "3:4", "4:3", "9:16", and "16:9". The default is "1:1".
- **personGeneration**: Allow the model to generate images of people. The following values are supported:
  - `"DONT_ALLOW"`: Block generation of images of people.
  - `"ALLOW_ADULT"`: Generate images of adults, but not children. This is the default.