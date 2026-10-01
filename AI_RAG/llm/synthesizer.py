import json


class Synthesizer:
    def __init__(self, llm):
        self.llm = llm

    def generate(self, prompt: str) -> dict:
        response = self.llm.generate(prompt)

        if not response or not response.strip():
            raise ValueError("LLM returned an empty response.")

        cleaned = response.strip()

        # Remove Markdown code fences if Gemini returns them
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()

            if lines[0].strip().startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            cleaned = "\n".join(lines).strip()

        try:
            result = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Gemini response is not valid JSON."
            ) from exc

        # Basic structure validation
        required_fields = {
            "answer",
            "evidence_ids",
            "confidence"
        }

        missing_fields = required_fields - result.keys()

        if missing_fields:
            raise ValueError(
                f"Missing required fields: {sorted(missing_fields)}"
            )

        if not isinstance(result["answer"], str):
            raise ValueError("The 'answer' field must be a string.")

        if not isinstance(result["evidence_ids"], list):
            raise ValueError("The 'evidence_ids' field must be a list.")

        if not isinstance(result["confidence"], (int, float)):
            raise ValueError(
                "The 'confidence' field must be a number."
            )

        return result