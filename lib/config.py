import yaml

def config(yaml_path):
  yaml_file = open(yaml_path, 'r')
  try:
    data = yaml.load(yaml_file, yaml.Loader)
  except AttributeError:
    data = yaml.load(yaml_file, yaml.CLoader)
  return data

if __name__ == '__main__':
  c = config('pyBotTV/config.yaml')
  print(c)
