#!/usr/bin/env python3.10
import asyncio
import iterm2

async def main(connection):
    app = await iterm2.async_get_app(connection)

    vl = "cpu_temp_use_fahrenheit"
    knobs = [iterm2.CheckboxKnob("Use fahrenheit", False, vl)]
    component = iterm2.StatusBarComponent(
        short_description="CPU Temp",
        detailed_description="Provides Apple Silicon CPU temperature",
        knobs=knobs,
        exemplar="🌡 69˚C",
        update_cadence=None,
        identifier="turch.in.cpu_temp")
    
    async def poll_cpu_temp():
        while True:
            cmd = '~/Library/Application\ Support/iTerm2/Scripts/AutoLaunch/smc'
            proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await proc.communicate()
            await proc.wait()
            await app.async_set_variable("user.cpu_temp", round(float(stdout.decode().strip()), 1) if not stderr else '--')
            await asyncio.sleep(2)
    
    global task
    task = asyncio.create_task(poll_cpu_temp())

    @iterm2.StatusBarRPC
    async def coro(knobs, temp=iterm2.Reference("iterm2.user.cpu_temp?")):
        if temp is None:
            return "Measuring"
        pattern = "🌡 {}˚C"
        if vl in knobs and knobs[vl]:
            pattern = "🌡 {}˚F"
        return [pattern.format(temp)]

    await component.async_register(connection, coro)

iterm2.run_forever(main)
