# AI-Powered Motor Insurance Advisor

### Project Description

The **AI-Powered Motor Insurance Advisor** is an intelligent, voice-based insurance assistance platform designed to help customers understand, compare, and select suitable motor insurance policies based on their individual requirements.

The platform combines a user-friendly website with an AI-powered calling agent to deliver a personalized insurance consultation experience, eliminating the need for customers to manually navigate complex policy documents or interact with traditional sales representatives.

### How It Works

**1. Customer Interest Registration**

Customers visit the website to explore motor insurance options, including comprehensive insurance, third-party insurance, and own-damage coverage. The website provides basic information about each category.

Interested customers submit their name and phone number, along with consent to receive an AI-assisted consultation call.

**2. AI-Initiated Customer Call**

After registration, the system automatically initiates an outbound call using Sarvam AI's voice technology.

The AI agent introduces itself, confirms the customer's interest, and starts a natural, interactive conversation in the customer's preferred language.

**3. Personalized Requirement Analysis**

The agent gathers relevant information through conversation, including:

- Vehicle type, make, model, and age.
- Existing insurance coverage and renewal status.
- Budget and preferred premium range.
- Driving habits and vehicle usage.
- Desired coverage, add-ons, and claim-related preferences.

Instead of following a rigid questionnaire, the agent adapts its questions based on the customer's responses.

**4. Knowledge-Based Insurance Consultation**

The system maintains a structured knowledge base containing insurance policy documents, brochures, coverage details, exclusions, terms and conditions, and add-on information from multiple insurance providers.

Using Retrieval-Augmented Generation (RAG), the AI agent retrieves relevant information from these documents to answer customer queries accurately.

Customers can ask questions such as:

- What is the difference between comprehensive and third-party insurance?
- Does this policy cover flood damage?
- Is zero-depreciation coverage worth purchasing?
- Which policy offers better coverage for my five-year-old car?
- What is excluded from this insurance policy?

The agent grounds its answers in the available policy documentation rather than relying solely on general LLM knowledge.

**5. Intelligent Policy Comparison and Recommendations**

Based on the customer's requirements, the system identifies and compares suitable insurance policies.

The AI explains the differences in coverage, exclusions, deductibles, add-ons, claim conditions, and available premium information.

Recommendations are personalized and supported by information from the knowledge base. Actual premiums and eligibility are obtained from insurer-approved quotation APIs where available, rather than being estimated by the LLM.

**6. Post-Call Summary and Follow-Up**

After the conversation, the system generates a structured summary containing:

- Customer and vehicle requirements.
- Key questions and concerns.
- Policies discussed and compared.
- Suitable policy options with supporting reasons.
- Customer interest and next steps.

The information is stored in a database and can be displayed on an administrative dashboard. The customer may also receive a summary or quotation link through an approved communication channel.

### Proposed Technology Stack

| Component | Technology |
|---|---|
| Customer website | Next.js / React |
| AI calling agent | Sarvam Voice Agents |
| Speech recognition | Sarvam Saaras |
| Conversational AI | Sarvam-hosted LLM |
| Voice synthesis | Sarvam Bulbul |
| Knowledge base | Sarvam Knowledge Bases / RAG |
| Backend and APIs | Python FastAPI |
| Database | PostgreSQL |
| Telephony | Sarvam-supported telephony / Exotel |
| Insurance quotations | Insurer APIs, where available |

### MVP Scope

The initial prototype will focus exclusively on **private car motor insurance in India**.

It will demonstrate an end-to-end workflow: customer registration, automated outbound calling, requirement collection, policy-document retrieval, conversational policy comparison, personalized suggestions, and post-call reporting.

The MVP can begin with a curated collection of real motor insurance policy documents and a limited set of providers. It will not require live policy purchasing or payment processing.

For the prototype, policy comparisons will be based on verified documentation and explicitly labeled sample premiums where actual quotations are unavailable.

### Project Objective

To build a scalable, multilingual, AI-powered insurance advisory experience that transforms traditional insurance discovery into a personalized conversation, making it easier for customers to understand policy terms, evaluate coverage options, and make informed insurance decisions.

The platform can subsequently be extended to health insurance, term life insurance, travel insurance, and other categories using the same underlying voice-agent architecture.

**Important regulatory consideration:** In India, personalized insurance recommendations, solicitation, and policy distribution may fall under IRDAI-regulated activities. A production deployment should operate through an appropriately licensed insurer or intermediary, with customer consent, disclosure of the AI agent's identity, and appropriate data-protection controls. The MVP should be positioned as an educational comparison and lead-assistance tool unless the necessary authorizations are in place.