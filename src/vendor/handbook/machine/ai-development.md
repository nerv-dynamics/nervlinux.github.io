# AI development

Running a language model on the machine with S2 and talking to it through OpenAI's API from any program, and PyTorch and CUDA in a container.

## S2

S2 is Nerv's inference engine. It runs a model on the GPU, reached through the compute fabric like any other program, and serves it to any number of programs at once: batched prefill and decode, speculative decoding with a drafter, a prefix cache that resumes a conversation where its last turn left off, and sampling on the device. It ships as one package:

```
$ doas dnf install nerv-s2
```

`s2 --help` lists every command, and `tldr s2` shows the ones you use most.

## The published models

Two models are published for S2, on Hugging Face, each converted for the GB10 and paired with a drafter. `s2 pull` lists them, and which are already here:

```
$ s2 pull
qwen3.8-27b                18.3 GB  Qwen3.8-27B in NVFP4, with the Inco DFlash2 drafter
qwen3.8-flash-next         72.3 GB  Qwen3.8-Flash-Next (125B MoE) in NVFP4, with PixelML's DFlash drafter
```

`qwen3.8-27b` is the dense model and the quicker download. `qwen3.8-flash-next` is a mixture of experts with 125 billion parameters, which fits on one GB10 because NVFP4 stores each weight in four bits.

## Fetching a model

```
$ s2 pull qwen3.8-27b
```

The files go into the model store, `~/.local/share/s2/models`. Each is checked against the SHA-256 that the `nerv-s2` package records for it, so a file is kept only if it is exactly the one published, whichever mirror it came from. An interrupted pull resumes where it stopped.

## Preparing a model for this GPU

```
$ s2 plan --model ~/.local/share/s2/models/Qwen3.8-27B-s2v9dp.s2w
```

A plan is the model laid out for this machine's GPU: every kernel launch, in order, at the shapes this model needs. Making one takes a few minutes of CPU, once per model, and it is kept in `~/.local/share/s2/plans` for every run after.

## The dashboard

`s2` on a terminal opens the dashboard: what the engine is running and how fast, its memory and its sessions, the models on disk, and a form that runs one. The form starts a model with OpenAI's API on this machine, ready for a client.

`s2 tcp:HOST:PORT` watches an engine running somewhere else.

## Serving a model

`s2 serve` runs the engine without the dashboard, and `--openai` serves OpenAI's chat completions API from inside it:

```
$ s2 serve --model ~/.local/share/s2/models/Qwen3.8-27B-s2v9dp.s2w \
    --draft ~/.local/share/s2/models/Qwen3.8-27B-dflash2-inco.s2w \
    --openai 127.0.0.1:8000
```

Any program that speaks OpenAI's API can use it, pointed at `http://127.0.0.1:8000/v1`:

```
$ curl -s http://127.0.0.1:8000/v1/chat/completions \
    -H 'Content-Type: application/json' \
    -d '{"messages": [{"role": "user", "content": "Name three Unix signals."}]}'
```

An answer without `max_tokens` ends at the model's end of turn or where its context does, as OpenAI's own API behaves.

`--positions N` bounds the context the engine will hold, and `--sessions N` how many conversations it serves at once. The drafter is optional; with it, the engine drafts several tokens ahead and the model checks them in one step, which makes decoding faster without changing the answer.

### One model across several GPUs

A model too slow on one GPU, or too large for it, can run across this machine's GPU and other machines' in the fleet. The model is cut into parts by heads and columns, one part per GPU, and the parts are joined after every layer through the compute fabric's NCCL; the drafter is cut the same way. It samples exactly as the whole model does. Make a plan for that many parts, then name the other machines as `axon run --on` names them:

```
$ s2 plan --model ~/.local/share/s2/models/Qwen3.8-27B-s2v9dp.s2w \
    --draft ~/.local/share/s2/models/Qwen3.8-27B-dflash2-inco.s2w --ranks 2
$ s2 serve --model ~/.local/share/s2/models/Qwen3.8-27B-s2v9dp.s2w \
    --draft ~/.local/share/s2/models/Qwen3.8-27B-dflash2-inco.s2w \
    --peers eva-00 --openai 127.0.0.1:8000
```

A plan for several parts is kept beside the one-GPU plan, and `serve` takes the one for itself and its peers.

A dense model splits this way today; a mixture of experts, split by its experts, is on the roadmap.

Every step crosses between the machines twice per layer, so this pays only over a direct link between them. Two GB10s joined by their ConnectX ports decoded Qwen3.8-27B with its drafter at 77.7 tokens a second, against 45.9 on one of them (eight held-out prompts of 255 tokens each, November 2026).

`s2 catalog` prints, as JSON, the models, drafters and plans this machine has and the GPUs it can reach, for scripts.

## PyTorch and CUDA

PyTorch, and anything else built on the CUDA runtime, runs in a container with the machine's GPU. [The GPU in a container](containers.md#the-gpu-in-a-container) shows PyTorch's own CUDA build training on it.
