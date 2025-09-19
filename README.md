# Resarch Paper Translator
This is an AI based software to translate a research paper from English to Bengali

## Project Structure
The project is divided into following parts:
- models
- controllers
- services

```text
├── controllers
│   └── gemini_translation_controller.py
├── models
│   ├── GeminiTranslationModel.py
│   ├── TranslationModel.py
│   └── Translation.py
├── services
│   ├── gemini_translation_service_impl.py
│   └── translation_service.py
├── Makefile
├── README.md
├── requirements.txt
└── server.py
```

### Models
Model represents real world entity.
Example: `Translation` is a model that represents the translation of a text.


`TranslationModel` is an AI model that is used to translate the research paper.`TranslationModel` is a base class. You need to extend the base class according to your needs. 
Example: `GeminiTranslationModel` extends `TranslationModel` to include model name and API key. Because if you want to work with Gemini API you need to provide the model name and API key.


### Services
Services are the main logic to perform a task. Eg: `TranslationService` is used to translate text.

`TranslationService` is used to translate text from English to Bengali. It is an abstract class. So, you need to make a concrete implementation of `TranslationService` to use it. `TranslationService` provides a `translate(original_text)` method to translate. 

Example: `GeminiTranslationService` implements `translate(original_text)` method to translate text using Gemini API.

### Controllers
Controllers deal with HTTP requests and routing.


## How to run
To run the project use the following stepos.
1. Create a virtual environment.
    ```bash
    python -m venv venv
    ```
2. Activate the virtual environment.
    ```bash
    source venv/bin/activate
    ```
3. Install dependencies.
    ```bash
    pip install -r requirements.txt
    ```
4. Run the server.
    For `dev` mode:
    ```bash
    fastapi dev server.py
    ```

    For `prod` mode:
    ```bash 
    fastapi run server.py
    ```
5. Test
    Use `http://localhost:8000/docs` to test the API.



