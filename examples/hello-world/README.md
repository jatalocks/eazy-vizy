##### Parameters

The parameters are taken from `eazyvizy.yaml`:

```yaml
parameters:
  - default: mytext
    name: string-param
    type: text
  - default: 0
    name: number-param
    type: number
  - choices: [a, b, c, d]
    default: b
    name: single-choice-param
    type: single-choice
  - choices: [e, f, g, h]
    default: [e, g]
    name: multi-choice-param
    type: multi-choice
```

##### Python Endpoints

Each function annotated with `@eazyvizy.endpoint` in the `__init__.py` in the `code` folder corresponds to a route you can access in GET/POST requests:

```python
import random
import eazyvizy

@eazyvizy.endpoint
def run(**kwargs):
    print("starting")
    return "Started"

@eazyvizy.endpoint
def log(**kwargs):
    done = random.choice([True, False])
    if not done:
        return "Not done yet. This is a log.", 425
    return "Done!",200

@eazyvizy.endpoint
def res(**kwargs):
    print("resulting")
    return "Result"
```
