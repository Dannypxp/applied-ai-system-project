Original Project : PawlPal+ - Module 2

The original goal of Pawlpal was to provide an app to pet owners that allows them to input all their tasks for their given pet and generate a priority based schedule with a complex scheduling algorithim. Futhermore, AI was used to create and implement the scheduling algorithim with a CLI first approach and then connecting a GUI to the app.

Title : PawPal Ultra
Summary: My project takes the original PawPal+ and makes it alot more pet owner friendly by adding a "ask question" section for common questions about their pet (currently only supports cats). The question feature uses a rag implementation for data retrieval with three options that are retrival only on internal documentation , retrieval with gemini support or only Gemini plus documenatation. Futhermore, I made some GUI changes by adding the option to support multiple pets, a table containing all pets added and more frequencies for tasks (monthly and yearly.)


System design:

The system design is fairly simple for the rag system, first user inputs their question, secondly the rag system loads internal documentation, next the user input is indexed and used to search through internal documentation, lastly gemini takes over if the retrival system cannot make a confident answer.

User input and Internal Docs -> Rag System -> retrival -> Answer or Not sure -> gemini -> profit
   |
profit


Setup Directions
First:

    Make a .env file and paste this text with your own gemini API key
    - GEMINI_API_KEY=Your_Gemini_API_key

Second:

    Make a virutal environment
    - python3 -m venv .venv 

Third:

    Install Requirments
    - pip install -r requirements.txt

Fourth:

    Run app.py with StreamLit
    - python3 -m streamlit run app.py

Fifth:

    Enjoy :D


Sample Interactions:

Retrieval Only
Test 1:

    Input: Why is my cat coughin

    Output: I don't know.

Test 2:

    Input: Which cat breed is the most playful

    Output: [cat_health_rag.md] Common questions:

    How can I tell if my cat is overweight? — You should easily feel ribs without pressing hard; if you cannot, the cat is likely overweight.
    How do I help my cat lose weight safely? — Gradual calorie reduction (no more than 1–2% body weight loss per week); rapid weight loss causes hepatic lipidosis.
    Can neutering cause weight gain in cats? — Yes; neutering reduces metabolic rate by approximately 20–30%; adjust food portions accordingly.
    What is the ideal weight for a cat? — Varies by breed; most domestic shorthair cats have an ideal weight of 3.5–5 kg (8–11 lbs).
    [cat_breeds_rag.md]

    Breed	Energy Level	Vocality	Independence	Affection
    Persian	Very Low	Very Low	High	Moderate
    Ragdoll	Low	Low	Low	Very High
    British Shorthair	Low	Low	High	Moderate
    Russian Blue	Low–Moderate	Low	Moderate	High (selective)
    Maine Coon	Moderate	Moderate	Moderate	High
    Norwegian Forest Cat	Moderate	Low	Moderate–High	Moderate
    Birman	Moderate	Low–Moderate	Moderate	High
    Burmese	Moderate–High	Moderate	Very Low	Very High
    Siamese	Moderate–High	Very High	Low	High
    Abyssinian	Very High	Moderate	Moderate	Moderate
    Bengal	Very High	Moderate–High	Moderate	Moderate
    Devon Rex	High	Moderate	Low	Very High
    Turkish Angora	High	Moderate	Moderate	High
    Domestic Shorthair	Variable	Variable	Variable	Variable
    Domestic Longhair	Variable	Variable	Variable	Variable
    Domestic Mediumhair	Variable	Variable	Variable	Variable
    [cat_breeds_rag.md]

    Breed	Coat Length	Grooming Frequency	Matting Risk
    Sphynx	Hairless	Weekly bath	N/A (skin care)
    Siamese	Short	Low (weekly brush)	Very Low
    British Shorthair	Short	Low–Moderate	Very Low
    Russian Blue	Short	Low–Moderate	Very Low
    Devon Rex	Very Short/Curly	Low	Low
    Abyssinian	Short	Low	Very Low
    Burmese	Short	Low	Very Low
    Birman	Semi-Long	Moderate (weekly)	Low
    Turkish Angora	Long (single coat)	Moderate	Low
    Maine Coon	Long	Moderate (2–3x/week)	Moderate
    Norwegian Forest Cat	Long	Moderate (2–3x/week)	Moderate
    Ragdoll	Semi-Long	Moderate	Low–Moderate
    Persian	Long	High (daily)	Very High
    Domestic Shorthair	Short	Low (weekly brush)	Very Low
    Domestic Mediumhair	Medium	Moderate (1–2x/week)	Low–Moderate
    Domestic Longhair	Long	Moderate (2–3x/week)	Moderate

    

Retrieval and Gemini Fallback
Test 1:

    Input: Why is my cat coughin

    Output: Oh no, hearing your cat cough can definitely be concerning! There are several reasons why your feline friend might be clearing their throat.

    Common reasons often include:

    Hairballs: This is a very frequent cause, as cats often cough and gag to expel accumulated fur.
    Irritants: Dust, smoke, strong smells, or even certain allergens can irritate their airways.
    However, it could also be a sign of something that needs a vet's attention, such as:

    Respiratory infections: Like a cold or flu.
    Feline asthma: A common condition that can cause coughing.
    Other underlying medical issues.
    What to do: If the coughing is frequent, persistent, or if you notice any other symptoms like lethargy, loss of appetite, or difficulty breathing, it's always best to schedule a visit with your veterinarian. They can properly diagnose the cause and get your cat feeling better!

    Keeping track of when the coughing started and how often it happens can be very useful information for your vet.

    Answer sourced from Gemini general knowledge (not internal docs).

Test 2:

    Input: Which cat breed is the most playful

    Output: Based on our documentation, the Abyssinian and Bengal cat breeds are noted for having a "Very High" energy level, which suggests they are among the most playful! (Source: cat_breeds_rag.md)

    Answer sourced from internal documentation.


Desgin Decisions:

I built PawPal Ultra with the RAG system because I wanted the app to come with accurate answers for pet owners who might have urgent questions about their pets behavior or certain health symptons. Using the rag system allows me to use internal documentation to minimize the usage of outside llms, but whenever the retriaval algorithim or internal documenation lacks the confidence to answer a question, the user input and documentation is fowarded to gemini to fix the response. The trade off is the gemini usage because someone with a free plan(like myself) only has a limited amount of responses.


Testing Summary:

What works well is the gemini implemenatation which provides accurate information to answer pet owner questions. What didnt work as well was the retreival only method which even being a simple algorithim compared to the LLM, struggles to respond with information anywhere near the users question.


Reflection:

This project has taught me that AI can really be used for any purpose if you set the right restrictions and give it the right context. But more importantly how AI has really made code easier to write, learn, understand and tweak. What I mean is that using claude in this project turned this potentially week long project into a couple of hours.


Reliability and Evaluation:

Pytest was used for testing in the test_rag_retrieval.py file


Reflection and Ethics:

    Limitations and Biases:
    - The internal documentation is only limited to cats
    - App is biased towards cats

    Can the AI be misused:
    - The Gemini credits can be misused by spamming questions and running out
    - Gemini ignores questions not in context

    What surprised me:
    - It runs out of credits quickly

    Collaboration with AI:
    - The AI used to help build this project was claude and it was extremely helpful explaining the existing code and suggesting fixes to problems with connecting all the python files to the GUI. One extremely helpful instance was when claude explained how the rag system from a prior project will work exceptionally well with my use case for this system, this dramatically reduced my time having to create one for scratch.

Loom video with Demo of Pawpal Ultra
https://www.loom.com/share/a67ff884241d4cfbbc7a915192f2fdea

