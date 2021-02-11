## Why drytoml?

### A bit of History

We wanted to have a single source of truth where code style and convetions live.
Because of its nature, it should be an evolving thing, as we found more edge cases, or
decided to use another framkework to solve a specific problem.

Using tools like cookiecutter and nitpick cover part of the solution, which is why we
deceided to develop drytoml.


### Driving principles

* Use `.toml` as configuration file, with `pyproject.toml` as default, unless specified.
* Allow inheritance (transclusion) of configurations both from path and from urls.
* Allow as much overriding / customization as possible.
* Enable update of references, but disable them by default.
