import json
import os
from textwrap import dedent

import streamlit as st
import streamlit.components.v1 as components


def read_setting(*keys: str) -> str:
    for key in keys:
        value = os.getenv(key)
        if value:
            return value

        try:
            value = st.secrets[key]
        except Exception:
            value = None

        if value:
            return str(value)

    return ""


st.set_page_config(
    page_title="PGIS 접근성 지도",
    layout="wide",
    initial_sidebar_state="collapsed",
)

supabase_url = read_setting("SUPABASE_URL", "NEXT_PUBLIC_SUPABASE_URL")
supabase_anon_key = read_setting("SUPABASE_ANON_KEY", "NEXT_PUBLIC_SUPABASE_ANON_KEY")

config = json.dumps(
    {
        "supabaseUrl": supabase_url,
        "supabaseAnonKey": supabase_anon_key,
    },
    ensure_ascii=False,
)

st.markdown(
    """
    <style>
      .stApp {
        margin: 0;
        padding: 0;
      }

      .block-container {
        max-width: none;
        padding: 0;
      }

      header,
      footer,
      [data-testid="stToolbar"],
      [data-testid="stDecoration"],
      [data-testid="stStatusWidget"] {
        display: none !important;
      }

      iframe {
        display: block;
        min-height: 100vh !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

html = dedent(
    f"""
    <!doctype html>
    <html lang="ko">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link
          rel="stylesheet"
          href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          integrity="sha256-p4NxAoJBhIINfQnC8HLv8iGICK0vrsR9gZlB5Q7Eq9A="
          crossorigin=""
        />
        <style>
          html,
          body {{
            width: 100%;
            height: 100%;
            margin: 0;
            overflow: hidden;
            font-family: Arial, Helvetica, sans-serif;
          }}

          #app {{
            position: fixed;
            inset: 0;
            width: 100vw;
            height: 100vh;
            background: #eef1f2;
          }}

          #map {{
            position: absolute;
            inset: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
          }}

          .marker-dot {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border: 2px solid white;
            box-sizing: border-box;
          }}

          .marker-form {{
            position: absolute;
            top: 20px;
            left: 20px;
            z-index: 2000;
            display: none;
            background: white;
            padding: 10px;
            color: #111;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.24);
          }}

          .marker-form.is-open {{
            display: block;
          }}

          .marker-form h3 {{
            margin: 0 0 12px;
            font-size: 18px;
            line-height: 1.2;
          }}

          .marker-form input[type="text"] {{
            width: 170px;
            height: 28px;
            box-sizing: border-box;
            margin-bottom: 8px;
            padding: 3px 6px;
            border: 1px solid #999;
            font-size: 14px;
          }}

          .marker-form label {{
            display: block;
            margin: 4px 0;
            font-size: 14px;
            white-space: nowrap;
          }}

          .marker-form input[type="checkbox"] {{
            margin: 0 5px 0 0;
            vertical-align: middle;
          }}

          .marker-form button {{
            min-width: 48px;
            margin-top: 8px;
            padding: 4px 9px;
            border: 1px solid #767676;
            border-radius: 2px;
            background: #f0f0f0;
            color: #111;
            font-size: 14px;
            cursor: pointer;
          }}

          .marker-form button:disabled {{
            cursor: wait;
            opacity: 0.65;
          }}

          .legend {{
            position: absolute;
            bottom: 20px;
            left: 20px;
            z-index: 1000;
            background: white;
            padding: 10px 12px;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
            color: #111;
            font-size: 14px;
          }}

          .legend-title {{
            margin-bottom: 5px;
            font-weight: bold;
          }}

          .legend-row {{
            display: flex;
            align-items: center;
            margin-bottom: 4px;
            white-space: nowrap;
          }}

          .legend-row:last-child {{
            margin-bottom: 0;
          }}

          .legend-dot {{
            width: 12px;
            height: 12px;
            margin-right: 6px;
            border-radius: 50%;
            flex: 0 0 auto;
          }}

          .status {{
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 2000;
            display: none;
            max-width: 360px;
            box-sizing: border-box;
            background: white;
            padding: 10px 12px;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.28);
            color: #111;
            font-size: 14px;
            line-height: 1.45;
          }}

          .status.is-open {{
            display: block;
          }}

          .status.is-error {{
            border-left: 4px solid #e74c3c;
          }}

          @media (max-width: 520px) {{
            .marker-form,
            .legend {{
              left: 12px;
            }}

            .marker-form {{
              top: 12px;
            }}

            .legend {{
              bottom: 12px;
              font-size: 13px;
            }}

            .status {{
              top: 12px;
              right: 12px;
              left: 12px;
              max-width: none;
            }}
          }}
        </style>
      </head>
      <body>
        <div id="app">
          <div id="map"></div>

          <form id="markerForm" class="marker-form">
            <h3>정보 등록</h3>
            <input id="stationName" type="text" placeholder="이름" />
            <label>
              <input id="tactile" type="checkbox" />
              점자블럭
            </label>
            <label>
              <input id="braille" type="checkbox" />
              점자노선도
            </label>
            <label>
              <input id="elevator" type="checkbox" />
              엘리베이터
            </label>
            <button id="saveButton" type="submit">저장</button>
          </form>

          <div class="legend">
            <div class="legend-title">접근성 등급</div>
            <div class="legend-row">
              <span class="legend-dot" style="background:#2ecc71"></span>
              매우 우수 (90+)
            </div>
            <div class="legend-row">
              <span class="legend-dot" style="background:#e9ec69"></span>
              양호 (70+)
            </div>
            <div class="legend-row">
              <span class="legend-dot" style="background:#f39c12"></span>
              보통 (50+)
            </div>
            <div class="legend-row">
              <span class="legend-dot" style="background:#e74c3c"></span>
              미흡 (30+)
            </div>
            <div class="legend-row">
              <span class="legend-dot" style="background:#2c3e50"></span>
              이용 어려움
            </div>
          </div>

          <div id="status" class="status"></div>
        </div>

        <script
          src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
          integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
          crossorigin=""
        ></script>
        <script>
          const CONFIG = {config};
          const map = L.map("map").setView([37.5665, 126.978], 13);
          const markerLayer = L.layerGroup().addTo(map);
          const markerForm = document.getElementById("markerForm");
          const stationName = document.getElementById("stationName");
          const tactile = document.getElementById("tactile");
          const braille = document.getElementById("braille");
          const elevator = document.getElementById("elevator");
          const saveButton = document.getElementById("saveButton");
          const statusBox = document.getElementById("status");
          let selectedPosition = null;

          L.tileLayer("https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png", {{
            maxZoom: 19,
          }}).addTo(map);

          window.addEventListener("resize", () => {{
            map.invalidateSize();
          }});

          function getColor(score) {{
            if (score >= 90) return "#2ecc71";
            if (score >= 70) return "#e9ec69";
            if (score >= 50) return "#f39c12";
            if (score >= 30) return "#e74c3c";
            return "#2c3e50";
          }}

          function getCustomMarker(score) {{
            return L.divIcon({{
              className: "",
              html: `<div class="marker-dot" style="background:${{getColor(score)}}"></div>`,
              iconSize: [20, 20],
              iconAnchor: [10, 10],
            }});
          }}

          function calcScore() {{
            let score = 0;
            if (tactile.checked) score += 40;
            if (braille.checked) score += 25;
            if (elevator.checked) score += 20;
            return score;
          }}

          function escapeHtml(value) {{
            return String(value ?? "")
              .replace(/&/g, "&amp;")
              .replace(/</g, "&lt;")
              .replace(/>/g, "&gt;")
              .replace(/"/g, "&quot;")
              .replace(/'/g, "&#039;");
          }}

          function showStatus(message, isError = false) {{
            statusBox.innerHTML = message;
            statusBox.classList.add("is-open");
            statusBox.classList.toggle("is-error", isError);
          }}

          function clearStatus() {{
            statusBox.classList.remove("is-open", "is-error");
            statusBox.innerHTML = "";
          }}

          function supabaseHeaders(extra = {{}}) {{
            return {{
              apikey: CONFIG.supabaseAnonKey,
              Authorization: `Bearer ${{CONFIG.supabaseAnonKey}}`,
              ...extra,
            }};
          }}

          function assertSupabaseConfig() {{
            if (!CONFIG.supabaseUrl || !CONFIG.supabaseAnonKey) {{
              showStatus(
                "Supabase 환경변수가 설정되지 않았습니다.<br />SUPABASE_URL / SUPABASE_ANON_KEY 또는 NEXT_PUBLIC_SUPABASE_URL / NEXT_PUBLIC_SUPABASE_ANON_KEY를 설정해주세요.",
                true,
              );
              return false;
            }}

            return true;
          }}

          function addMarker(station) {{
            const lat = Number(station.lat);
            const lng = Number(station.lng);
            const score = Number(station.score || 0);

            if (!Number.isFinite(lat) || !Number.isFinite(lng)) return;

            const status = score >= 70 ? "양호 이상" : "개선 필요";
            L.marker([lat, lng], {{ icon: getCustomMarker(score) }})
              .bindPopup(
                `<b>${{escapeHtml(station.name)}}</b><br />` +
                `접근성 점수: <b>${{escapeHtml(score)}}</b><br />` +
                `상태: ${{status}}`,
              )
              .addTo(markerLayer);
          }}

          async function loadStations() {{
            if (!assertSupabaseConfig()) return;

            try {{
              clearStatus();
              const response = await fetch(
                `${{CONFIG.supabaseUrl}}/rest/v1/stations?select=*`,
                {{
                  headers: supabaseHeaders(),
                }},
              );

              if (!response.ok) {{
                throw new Error(await response.text());
              }}

              const data = await response.json();
              markerLayer.clearLayers();
              data.forEach(addMarker);
            }} catch (error) {{
              showStatus(`데이터를 불러오지 못했습니다.<br />${{escapeHtml(error.message)}}`, true);
            }}
          }}

          function openForm(latlng) {{
            selectedPosition = latlng;
            stationName.value = "";
            tactile.checked = false;
            braille.checked = false;
            elevator.checked = false;
            markerForm.classList.add("is-open");
            stationName.focus();
          }}

          function closeForm() {{
            selectedPosition = null;
            markerForm.classList.remove("is-open");
          }}

          map.on("click", (event) => {{
            openForm(event.latlng);
          }});

          markerForm.addEventListener("submit", async (event) => {{
            event.preventDefault();
            if (!selectedPosition || !assertSupabaseConfig()) return;

            const payload = [{{
              name: stationName.value,
              lat: selectedPosition.lat,
              lng: selectedPosition.lng,
              tactile_block: tactile.checked,
              braille_map: braille.checked,
              elevator: elevator.checked,
              score: calcScore(),
            }}];

            try {{
              saveButton.disabled = true;
              const response = await fetch(`${{CONFIG.supabaseUrl}}/rest/v1/stations`, {{
                method: "POST",
                headers: supabaseHeaders({{
                  "Content-Type": "application/json",
                  Prefer: "return=representation",
                }}),
                body: JSON.stringify(payload),
              }});

              if (!response.ok) {{
                throw new Error(await response.text());
              }}

              closeForm();
              await loadStations();
            }} catch (error) {{
              showStatus(`저장하지 못했습니다.<br />${{escapeHtml(error.message)}}`, true);
            }} finally {{
              saveButton.disabled = false;
            }}
          }});

          loadStations();
        </script>
      </body>
    </html>
    """
)

components.html(html, height=900, scrolling=False)
