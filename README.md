# EasyCare: AI-Powered Healthcare Voice Agent

Welcome to **EasyCare**, a conceptual healthcare assistant designed to streamline the patient appointment process, reduce wait times, and optimize healthcare workflows. By leveraging the power of **aiXplain**, **retell.ai**, and **AWS Lambda**, this system demonstrates the potential of AI in real-world healthcare scenarios.

---

## Table of Contents

- [Overview](#overview)
- [Setup Guide](#setup-guide)
  - [Prerequisites](#prerequisites)
  - [Building the lambda function Layer](#building-the-lambda-function-layer)
- [Repository Structure](#repository-structure)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

EasyCare provides an end-to-end solution for managing patient appointments and pre-appointment diagnostics. The workflow is as follows:

1. A patient calls the clinic's phone number, which is connected to a **retell.ai** voice agent.
2. The voice agent interacts with the patient, collects symptoms, and transcribes the conversation.
3. The transcription is sent via a webhook to an **AWS Lambda** function.
4. The Lambda function processes the data using an **aiXplain pipeline**, which:
   - Summarizes the problem.
   - Extracts key patient details (name, age, pain scale).
   - Determines if pre-appointment tests like bloodwork or MRIs are needed.
5. Results are stored and visualized via **Senso**, enabling doctors to review before the patient’s visit.

---


## Prerequisites

- **Python** installed (>=3.8 recommended).
- **Docker** installed for creating the Lambda function layer.
- An **AWS Account** for deploying Lambda.
- Access to **aiXplain** and **retell.ai** accounts.
- An **API Key** for Senso integration.

## Building the lambda function Layer

```bash
docker build --platform linux/amd64 -t easycare-image:latest .
docker run --platform linux/amd64 --name temp-container easycare-image:latest
docker cp temp-container:/workspace/easycare/python ./python
docker rm temp-container
```
Zip the python directory and upload it as a layer in the AWS Lambda Console.

## Repository Structure
```plaintext
easycare/
├── Dockerfile                 # Docker configuration for Lambda layer
├── lambda_function.py         # AWS Lambda handler
├── requirements.txt           # Dependencies for the Lambda function
├── aiXplain_pipeline.json     # Exported aiXplain pipeline configuration
├── README.md                  # Project documentation (this file)
```

## Usage

1. Set up the system by following the Setup Guide <INSERT AIXPLAIN SETUP GUIDE LINK> .
2. Deploy the Lambda function and connect it to the retell.ai webhook.
3. Test the voice agent by calling the assigned phone number.
4. Monitor outputs in aiXplain and Senso for insights and summaries.

## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests for improvements or new features.

## License

This project is licensed under the MIT License.
