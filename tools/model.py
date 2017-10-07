#

from util import ModHostConnection
from util import get_plugins
from util import get_jack_client
# from util import get_ports
from util import get_symbols
from util import connect_effect


class Model:

  def __init__(self):
    self.plugins_slots = {}

    #
    self.plugins, self.plugin_map = get_plugins()

    #
    self.mod_host = ModHostConnection()

    #
    self.jack_client = get_jack_client('lilt_jack_client')


  def get_plugin_urls(self):
    return [p.get_uri() for p in self.plugins]


  def clear_modules(self):
    for i in range(len(self.plugins_slots)):
      self.clear_module(i)


  def clear_module(self, i):
    self.mod_host.remove_plugin(i)
    self.plugins_slots[i] = ''


  # def add_modules(self, plugins):
  #   for i in range(16):
  #     self.mod_host.send_command('remove {}'.format(i))
  #   for i, plugin in enumerate(plugins):
  #     # self.mod_host.send_command('remove {}'.format(selection))
  #     # self.mod_host.send_command('add {} {}'.format(value, selection))
  #     # self.mod_host.send_command('remove {}'.format(i))
  #     self.mod_host.send_command('add {} {}'.format(plugin, i))
  #     # self.mod_host.get_presets(value)
  #
  #   connect_audio_midi(self.jack_client)


  def add_module(self, url, i):
    self.mod_host.remove_plugin(i)
    self.mod_host.add_plugin(url, i)

    self.plugins_slots[i] = url

    connect_effect(self.jack_client, 'effect_{}'.format(i))


  def get_param(self, channel, symbol):
    return self.mod_host.get_param(channel, symbol)


  def set_param(self, channel, symbol, value):
    self.mod_host.set_param(channel, symbol, value)


  def get_symbols(self, url):
    plugin = self.plugin_map[url]
    return get_symbols(plugin)


  def get_instances(self):
    return self.plugins_slots
