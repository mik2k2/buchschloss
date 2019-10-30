"""Auto-create a form from a peewee model"""

import peewee
import runpy
import argparse

FIELD_MAP = {
    peewee.IntegerField: 'IntEntry',
    peewee.CharField: 'Entry',
    peewee.BooleanField: 'CheckbuttonWithVar',
    peewee.Field: '...'  # since apping are orderen, this is a catch-all
}

def create_form(model,
                element='{name}: mtkf.Element = {field}',
                form_header='class {model}Form(mtkf.Form):'):
    suite = [form_header.format(model=model.__name__)]
    for name in vars(model):
        # avoid k, v in vars(model).items()
        # as fields are descriptors
        # aviof dir because we want nice ordered results
        field = getattr(model, name)
        if not isinstance(field, peewee.Field):
            continue
        for k, v in FIELD_MAP.items():
            if isinstance(field, k):
                suite.append(element.format(name=name, field=v))
                break
    return '\n    '.join(suite)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    parser.add_argument('--element', default='{name}: mtkf.Element = {field}')
    parser.add_argument('--form-header', default='class {model}Form(mtkf.Form):')
    parser.add_argument('--output')
    parser.add_argument('--encoding', default='UTF-8')
    args = parser.parse_args()
    ns = runpy.run_path(args.file)
    forms = ['"""These forms were autogenerated from the models in {} by {}"""'
             .format(args.file, __file__)]
    for mod in ns.values():
        if isinstance(mod, type) and issubclass(mod, peewee.Model):
            forms.append(create_form(mod, args.element, args.form_header))
    result = '\n\n\n'.join(forms)
    if args.output == '-':
        print(result)
    elif args.output:
        with open(args.output, 'w', encoding=args.encoding) as f:
            f.write(result)
    else:
        with open(args.file+'.autogen') as f:
            f.write(result)