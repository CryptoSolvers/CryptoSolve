# Libraries for Symbolic Methods

To get started you should make sure that your environment is setup.

<u>Clone the repository</u>
```bash
git clone https://<username>@bitbucket.org/marshall_am/moe_code.git
cd umw_crypto
```

<u>Create a virtual environment</u>

```bash
python3 -m venv senv
```

<u>Set your terminal session to use that environment</u>

```bash
source senv/bin/activate
```

<u>Install moe package</u>

```bash
./install_packages
```

If you encounter any permission errors, edit the file to look like the following instead,
```bash
pip install --user directoryname/
```

Now you can run the examples! In the future, don't forget to `source` the environment every time you open a new terminal session.

The following commands are then in your path:
- moe_tool : Runs the command line version of the tool
- moe_website : Runs the website version of the tool
- view_notebook : Runs a jupyter lab notebook with the example scripts 

## Libraries Included

### Algebra

A free algebra library that only exists as a way to encode equations such as `f(x) = 5` for later use in the other libraries.

Check out `algebra/README.md` for more information.

## Rewrite

Module that contains rewrite rules and variants.

## Unification

Module that contains different unification algorithms.
