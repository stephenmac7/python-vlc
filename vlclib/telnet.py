# Library for contacting VLC through telnet.

# Imports
import telnetlib
import re
from subprocess import PIPE, Popen

# Error Imports
from socket import error as sockerr

# Exceptions
class VLCProcessError(Exception):
  """Something is wrong with VLC itself."""
  pass

class CommandError(Exception):
  """Something is wrong with the command."""
  pass

class ParseError(Exception):
  """Could not parse the information provided by VLC."""
  pass

class LuaError(Exception):
  """Problem with the VLC lua telnet."""
  pass

class ConnectionError(Exception):
  """Something is wrong with the connection to VLC."""
  pass

# VLC Telnet Class
class VLCTelnet(object):
  """Conection to VLC using Telnet."""
  ## Non commands
  def __init__(self, host="localhost", password="admin", port=4212):
    # Make sure VLC is open at the moment by using pidof. Otherwise raise VLCProcessError.
    vlc_pidof = Popen("pidof vlc", shell=True, stdout=PIPE).stdout
    if vlc_pidof.read().decode().replace("\n", "") == "":
      raise VLCProcessError("No VLC Instance.")
    # Connect to telnet. Host and port are __init__ arguments
    try:
      self.tn = telnetlib.Telnet(host, port=port)
    except sockerr:
      raise ConnectionError("Could not connect to VLC Telnet. Make sure the Telnet interface is on.")
    # Login to VLC using password provided in the arguments
    self.tn.read_until(b"Password: ")
    self.run_command(password)

  def run_command(self, command):
    """Run a command and return a list with the output lines."""
    # Put the command in a nice byte-encoded variable
    full_command = command.encode('ascii') + b'\n'
    # Write out the command to telnet
    self.tn.write(full_command)
    # Get the command output, decode it, and split out the junk
    command_output = self.tn.read_until(b'> ').decode('ascii').split('\r\n')[:-1]
    # Raise command error if VLC does not recognize the command.
    if command_output != []:
      command_error = re.match(r"Error in.*", command_output[0])
      if re.match("Unknown command `.*'\. Type `help' for help\.", command_output[0]):
        raise CommandError("Unkown Command")
      elif command_error:
        raise LuaError(command_error.group())
    # Return the split output of the command
    return command_output

  ## Commands
  # Block 1
  def add(self, xyz):
    """Add XYZ to playlist."""
    command = 'add ' + xyz
    self.run_command(command)

  def enqueue(self, xyz):
    """Queue XYZ to playlist."""
    command = 'enqueue ' + xyz
    self.run_command(command)
  
  # Todo: Must figure out the playlist, search, and key commands.

  def sd(self, service='show'):
    """Show services discovery or toggle.
       Returns True for enabled and False for Disabled."""
    if service == 'show':
      return self.run_command('sd')
    else:
      command = 'sd ' + service
      output = self.run_command(command)[0]
      if 'enabled.' in output:
        return True
      elif 'disabled.' in output:
        return False
      else:
        raise ParseError("Could not parse the output of sd.")

  def play(self):
    """Play stream."""
    self.run_command('play')

  def stop(self):
    """Stop stream."""
    self.run_command('stop')

  def next(self):
    """Next playlist item."""
    self.run_command('next')

  def prev(self):
    """Previous playlist item."""
    self.run_command('prev')

  def goto(self, item):
    """Goto item at index."""
    command = 'goto ' + item
    self.run_command(command)

  def repeat(self, switch=True, setting='on'):
    """Toggle playlist repeat."""
    if switch:
      self.run_command('repeat')
    else:
      command = 'repeat ' + setting
      self.run_command(command)

  def loop(self, switch=True, setting='on'):
    """Toggle playlist loop."""
    if switch:
      self.run_command('loop')
    else:
      command = 'loop ' + setting
      self.run_command(command)

  def random(self, switch=True, setting='on'):
    """Toggle playlist random."""
    if switch:
      self.run_command('random')
    else:
      command = 'random ' + setting
      self.run_command(command)

  def clear(self):
    """Clear the playlist."""
    self.run_command('clear')

  def status(self):
    """Current playlist status."""
    status_output = self.run_command('status')
    if len(status_output) == 3:
      inputloc = '%20'.join(status_output[0].split(' ')[3:-1])
      volume = status_output[1].split(' ')[3]
      state = status_output[2].split(' ')[2]
      returndict = {'input': inputloc, 'volume': volume, 'state': state}
    elif len(status_output) == 2:
      volume = status_output[0].split(' ')[3]
      state = status_output[1].split(' ')[2]
      returndict = {'volume': volume, 'state': state}
    else:
      raise ParseError("Could not get status.")
    return returndict

  def set_title(self, setto):
    """Set title in current item."""
    command = 'title ' + setto
    self.run_command(command)
    
  def title(self):
    """Get title in current item."""
    return self.run_command('title')[0]

  def title_n(self):
    """Next title in current item."""
    self.run_command('title_n')

  def title_p(self):
    """Previous title in current item."""
    self.run_command('title_p')

  def set_chapter(self, setto):
    """Set chapter in current item."""
    command = 'chapter ' + setto
    self.run_command(command)

  def chapter(self):
    """Get chapter in current item."""
    return self.run_command('chapter')[0]

  def chapter_n(self):
    """Next chapter in current item."""
    self.run_command('chapter_n')

  def chapter_p(self):
    """Previous chapter in current item."""
    self.run_command('chapter_p')

  # Block 2
  def seek(self, time):
    """Seek in seconds, for instance 'seek 12'."""
    command = 'seek ' + time
    self.run_command(command)

  def pause(self):
    """Toggle pause."""
    self.run_command('pause')

  def fastforward(self):
    """Set to maximum rate."""
    self.run_command('fastforward')

  def rewind(self):
    """Set to minimum rate."""
    self.run_command('rewind')

  def faster(self):
    """Faster playing of stream."""
    self.run_command('faster')

  def slower(self):
    """Slower playing of stream."""
    self.run_command('slower')

  def normal(self):
    """Normal playing of stream."""
    self.run_command('normal')

  def rate(self, newrate):
    """Set playback rate to value."""
    command = 'rate ' + newrate
    self.run_command(command)

  def frame(self):
    """Play frame by frame."""
    self.run_command('frame')

  def fullscreen(self, switch=True, setting='on'):
    """Toggle fullscreen."""
    if switch:
      self.run_command('f')
    else:
      command = 'f ' + setting
      self.run_command(command)

  def info(self):
    """Information about the current stream."""
    unparsed = [x for x in self.run_command('info') if x != '|']
    try:
      streams = [x.split(' ')[2] for x in [x for x in unparsed if x[0] == '+'][:-1]]
    except:
      raise ParseError("Could not get streams.")
    out_list = []
    start = 1
    for stream in streams:
      cur_stream = {'Stream': stream}
      first_char = '|'
      while first_char == '|':
        cur_stream[unparsed[start].split(': ')[0][2:]] = ''.join(unparsed[start].split(': ')[1:])
        start += 1
        first_char = unparsed[start][0]
      start += 1
      out_list.append(cur_stream)
    return out_list

  # Skipping stats
  def get_time(self):
    """Seconds elapsed since stream's beginning."""
    return self.run_command('get_time')[0]

  def is_playing(self):
    """True if a stream plays, False otherwise."""
    command_output = self.run_command('is_playing')[0]
    return True if command_output == '1' else False

  def get_title(self):
    """The title of the current stream."""
    return self.run_command('get_title')[0]

  def get_length(self):
    """The length of the current stream."""
    return self.run_command('get_length')[0]

  # Block 3
  def set_volume(self, setto):
    """Set audio volume."""
    command = 'volume ' + setto
    self.run_command(command)

  def volume(self):
    """Get audio volume."""
    return self.run_command('volume')[0]

  def volup(self, raiseby):
    """Raise audio volume X steps."""
    command + 'volup ' + raiseby
    self.run_command(command)

  def voldown(self, raiseby):
    """Lower audio volume X steps."""
    command + 'voldown ' + raiseby
    self.run_command(command)

  # The following 'get' commands ARE NOT PARSED! Must do later :D
  def set_adev(self, setto):
    """Set audio device."""
    command = 'adev ' + setto
    self.run_command(command)

  def adev(self):
    """Get audio device."""
    return self.run_command('adev')[0]

  def set_achan(self, setto):
    """Set audio channels."""
    command = 'achan ' + setto
    self.run_command(command)

  def achan(self):
    """Get audio channels."""
    return self.run_command('achan')[0]

  def set_atrack(self, setto):
    """Set audio track."""
    command = 'atrack ' + setto
    self.run_command(command)

  def atrack(self):
    """Get audio track."""
    return self.run_command('atrack')[0]

  def set_vtrack(self, setto):
    """Set video track."""
    command = 'vtrack ' + setto
    self.run_command(command)

  def vtrack(self):
    """Get video track."""
    return self.run_command('vtrack')[0]

  def set_vratio(self, setto):
    """Set video aspect ratio."""
    command = 'vratio ' + setto
    self.run_command(command)

  def vratio(self):
    """Get video aspect ratio."""
    return self.run_command('vratio')[0]

  def set_crop(self, setto):
    """Set video crop."""
    command = 'crop ' + setto
    self.run_command(command)

  def crop(self):
    """Get video crop."""
    return self.run_command('crop')[0]

  def set_zoom(self, setto):
    """Set video zoom."""
    command = 'zoom ' + setto
    self.run_command(command)

  def zoom(self):
    """Get video zoom."""
    return self.run_command('zoom')[0]

  def set_vdeinterlace(self, setto):
    """Set video deintelace."""
    command = 'vdeinterlace ' + setto
    self.run_command(command)

  def vdeinterlace(self):
    """Get video deintelace."""
    return self.run_command('vdeinterlace')[0]

  def set_vdeinterlace_mode(self, setto):
    """Set video deintelace mode."""
    command = 'vdeinterlace_mode ' + setto
    self.run_command(command)

  def vdeinterlace_mode(self):
    """Get video deintelace mode."""
    return self.run_command('vdeinterlace_mode')[0]

  def snapshot(self):
    """Take video snapshot."""
    self.run_command('snapshot')

  def set_strack(self, setto):
    """Set subtitles track."""
    command = 'strack ' + setto
    self.run_command(command)

  def strack(self):
    """Get subtitles track."""
    return self.run_command('strack')[0]

  # Block 4 - Skipping a few useless ones when using a library
  def vlm(self):
    """Load the VLM."""
    self.run_command('vlm')

  def logout(self):
    """Exit."""
    self.run_command('logout')

  def shutdown(self):
    """Shutdown VLC."""
    self.run_command('shutdown')
