import asyncio
import subprocess
import time

from pywizlight import wizlight, PilotBuilder, discovery
from datetime import datetime

BULB_IPS = ['10.10.200.12', '10.10.200.13', '10.10.200.14', '10.10.200.15']
COLOUR_TEMP = 3000
FULL_BRIGHTNESS = 255

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

  async def poll(self):
    self._state = await self.get_state()
    self._colour_temp = self._state.get_colortemp()

    # Call handlers
    await self.schedule_on(['mon','tue', 'wed', 'thu', 'fri'],'07:08', 0.5 * FULL_BRIGHTNESS)
    await self.schedule_on(['mon','tue', 'wed', 'thu', 'fri'],'07:10', 1 * FULL_BRIGHTNESS)
    await self.schedule_off(['mon','tue', 'wed', 'thu', 'fri'],'07:30')


  def get_colour_temp(self):
    return self._colour_temp

  def get_ip(self):
    return self._ip

  def _meets_schedule(self, days, time):
    current_day = datetime.now().strftime('%a').lower()
    current_time = datetime.now().strftime('%H:%M').lower()

    if current_day not in days or current_time != time:
      return False

    return True


  async def schedule_on(self, days, time, brightness):

    if not self._meets_schedule(days, time):
      return
    
    await self.set_colour(colour_temp=self._colour_temp, brightness=brightness)

  async def schedule_off(self, days, time):

    if not self._meets_schedule(days, time):
      return
    
    await self._wizlight.turn_off()



async def main():
  bulbs = []
  for ip in BULB_IPS:
    bulbs.append(PhillipsWiz(ip))

  while True:
    for bulb in bulbs:
      if ping(bulb.get_ip()):
        try:
          await bulb.poll()
          colour_temp = bulb.get_colour_temp()
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