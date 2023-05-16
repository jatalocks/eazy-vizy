

def endpoint(func, **kwargs):
    def inner(**kwargs):
        print("Starting eazyvizy endpoint")
        result = func(**kwargs)
        print("Finished eazyvizy endpoint")
        return result
    inner.endpoint = True
    return inner
