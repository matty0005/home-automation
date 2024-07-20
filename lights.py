import asyncio
import subprocess
import time

from pywizlight import wizlight, PilotBuilder, discovery

BULB_IPS = ['10.10.200.12', '10.10.200.13', '10.10.200.14', '10.10.200.15']
COLOUR_TEMP = 3000

def ping(ip):
  try:
    output = subprocess.run(['ping', '-c', '1', '-W', '1', ip], capture_output=True)
    return output.returncode == 0

  except Exception as e:
    print(f"An error occurred: {e}")
    return False

class PhillipsWiz():
  def __init__(self, ip):
    self._ip = ip
    self._wizlight = wizlight(ip)
    print(self._wizlight)

  async def set_colour(self, colour_temp=3000, brightness=255):
    print(f"Setting colour for {self._ip}")
    await self._wizlight.turn_on(PilotBuilder(brightness=brightness, colortemp=colour_temp))

  async def get_state(self):
    return await self._wizlight.updateState()

  async def get_colour_temp(self):
    state = await self.get_state()
    return state.get_colortemp()

  def get_ip(self):
    return self._ip


async def main():
  bulbs = []
  for ip in BULB_IPS:
    bulbs.append(PhillipsWiz(ip))

  while True:
    for bulb in bulbs:
      if ping(bulb.get_ip()):
        try:
          colour_temp = await bulb.get_colour_temp()
          print(colour_temp)
          if colour_temp != COLOUR_TEMP: 
            await bulb.set_colour(colour_temp=COLOUR_TEMP)
        except Exception as e:
          print(f"An error occurred: {e}")

    time.sleep(1)


def _main():
  loop = asyncio.get_event_loop()
  loop.run_until_complete(main())

if __name__ == '__main__':
  _main()