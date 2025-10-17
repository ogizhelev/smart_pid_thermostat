
3. Restart Home Assistant.

4. Go to  
**Settings → Devices & Services → “+ Add Integration” → Smart PID Thermostat**.

---

## ⚙️ Configuration via UI

When adding a new Smart PID Thermostat:

- 🏡 **Climates:** select one or multiple `climate` entities to control  
- 🌡 **Sensor:** select the ambient temperature sensor  
- 🎯 **Target temperature**: desired ambient temp (e.g., 22 °C)  
- 🧮 **Kp, Ki, Kd**: PID gains (see Tuning below)  
- 🧭 **Mode:** `auto`, `heat`, or `cool` (used for information; not hard-enforced)  
- 🪄 **Deadband**: tolerance zone to avoid unnecessary changes  
- 🕒 **Interval**: control loop frequency (default 60 s)  
- 🌙 **Night setback / restore** (optional):
- Set setback time & temperature (e.g., 23:00 → 18 °C)
- Set restore time & temperature (e.g., 06:30 → 23 °C)
- Optional restore fan mode (`auto`, `low`, `quiet`)

👉 You can edit everything later via **“Options”**.

---

## 🧰 UI Entities

After creating the integration, the following entities will appear:

| Entity Type | Purpose |
|-------------|---------|
| `switch` – *Enabled* | Enables/disables PID control |
| `number` – *Target Temperature* | Adjust target ambient temp |
| `number` – *Kp / Ki / Kd* | Live tuning of PID gains |
| `number` – *Deadband* | Adjust deadband tolerance |
| `button` – *Start/Stop Autotune* | Start relay auto-tune, stop & apply suggested gains |
| `sensor` – *Status* | Shows “running” or “autotuning” |

---

## 🧪 Auto PID Tuning

The controller includes a **relay auto-tuner**:

1. Press **Start Autotune**.  
The integration will modulate the setpoint around the target and measure response.

2. After several oscillations (can take several minutes, depending on your HVAC),
press **Stop Autotune & Apply**.

3. New Kp, Ki, Kd values are calculated using Ziegler–Nichols classic tuning
and automatically applied to the integration.

> 💡 Tip: Start with a moderate amplitude (default 0.5 °C) and stable HVAC conditions.

---

## 🌃 Night Setback & Morning Restore

You can define:

- **Setback time** & temperature → e.g. 23:00 → 18 °C  
- **Restore time** & temperature → e.g. 06:30 → 23 °C  
- Optional **restore fan mode** (e.g. `low`)

These events automatically adjust all linked climate entities at the configured times daily.

---

## 🧭 Control Logic

- The PID loop runs every `interval` seconds.
- It calculates the **error** = (target ambient temp – current ambient temp).
- PID output is interpreted as a **temperature offset** from the target.
- The climate entity’s **set temperature** is adjusted within the configured min/max range.
- If the error is within the **deadband**, no change is made.
- Works with multiple climates simultaneously.

---

## 🧮 PID Tuning Tips

- **Kp**: start around 0.5–1.0  
- **Ki**: small values help remove steady-state error (e.g., 0.01–0.1)  
- **Kd**: helps damp oscillations; can be 0 initially  
- Use **autotune** as a starting point, then fine-tune manually.
- For slow systems (e.g., floor heating), use lower gains and longer intervals.

---

## 🧰 Advanced

### Multiple climate support

You can assign **multiple climate entities** to a single PID controller.
All linked entities will receive the same computed set temperature and optional fan mode changes.

---

## 📜 Example Use Cases

- Maintain stable room temperature with a **split A/C** by adjusting its setpoint dynamically.
- Control **multiple units** in a zone with a single PID loop.
- Smooth control of **heat pumps** or fan coils.
- Use setback/restore for **energy savings overnight**.

---

## 🧼 Uninstallation

- Remove the integration from Home Assistant UI (Settings → Devices & Services).
- Delete the `custom_components/smart_pid_thermostat` folder.

---

## 🧑‍💻 Development Notes

- Built for Home Assistant 2025.  
- Written in Python 3.11+  
- Uses Config Flow, modern selectors, and HA entity platforms for clean UI integration.  
- Auto-tune based on relay method for Ku/Tu estimation.

---

## 📜 License

MIT License.  
Created by [@ogizhelev](https://github.com/ogizhelev).

---

## 🧭 Roadmap

- [ ] PID auto-tune visualization  
- [ ] Optional outdoor temperature compensation  
- [ ] Adaptive setback schedule  
- [ ] Advanced tuning modes (Cohen–Coon, IMC)

---

## 🫱 Contributing

PRs and improvements welcome!  

---

## 📎 Related

- [HASmartThermostat](https://github.com/ScratMan/HASmartThermostat) — inspiration
- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [PID Control – Wikipedia](https://en.wikipedia.org/wiki/PID_controller)

---

