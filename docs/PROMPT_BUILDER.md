# Prompt Builder Template

This page describes the five-block structure used to craft prompts for Codex and other LLM agents. Following this layout keeps instructions clear and reproducible.

## 1. Identity
Define the persona or expertise the model should assume. Keep it concise so subsequent sections remain focused.

## 2. Instructions
List the rules and steps the model must follow. Use bullet points whenever possible to make constraints explicit.

## 3. Context
Provide relevant background, variable names and API samples. Anything the model needs to know before acting should appear here.

## 4. Examples
Add one or more input/output pairs that illustrate the expected behaviour. Few-shot examples improve accuracy for complex tasks.

## 5. Question
State the final request. Summarise the action you want the model to perform and include any chain-of-thought cues.

Combine these sections in order when composing prompts. The multi-agent pipeline in [AGENTS.md](AGENTS.md) automatically generates each block, but this file serves as a quick reference when writing new prompts manually.
