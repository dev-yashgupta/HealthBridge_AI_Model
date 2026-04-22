const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const { Pool } = require('pg');
const dotenv = require('dotenv');
const path = require('path');

// Load .env from parent directory
dotenv.config({ path: path.join(__dirname, '../.env') });

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// DB connection
const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
});

// Basic check
pool.query('SELECT NOW()', (err, res) => {
  if (err) {
    console.error('PostgreSQL connection error', err.stack);
  } else {
    console.log('Connected to PostgreSQL database');
  }
});

// Diagnose Route
app.post('/api/diagnose', async (req, res) => {
  const { patient_id, symptoms } = req.body;
  if (!symptoms) {
    return res.status(400).json({ error: "Symptoms are required." });
  }

  // Path to api_bridge.py
  const scriptPath = path.join(__dirname, '../api_bridge.py');

  // Resolve python executable: prefer PYTHON_PATH env var, then common names
  const pythonExe = process.env.PYTHON_PATH || 'python';
  
  const pythonProcess = spawn(pythonExe, [scriptPath], {
    cwd: path.join(__dirname, '../'),
    env: { ...process.env }, // pass full environment so python gets GROK_API_KEY etc
  });

  let outputData = '';
  let errorData = '';

  pythonProcess.stdout.on('data', (data) => {
    outputData += data.toString();
  });

  pythonProcess.stderr.on('data', (data) => {
    errorData += data.toString();
  });

  pythonProcess.on('close', (code) => {
    if (code !== 0) {
       console.error(`Python script exited with code ${code}`);
       console.error(`Python stderr: ${errorData}`);
       // But sometimes Python writes logs to stdErr, so let's check if outputData has JSON
       if(!outputData) {
         return res.status(500).json({ error: "Diagnosis pipeline failed.", details: errorData });
       }
    }
    
    try {
      // Find JSON block in outputData in case there's garbage string
      const jsonStart = outputData.indexOf('{');
      const jsonEnd = outputData.lastIndexOf('}');
      if(jsonStart === -1 || jsonEnd === -1) {
          throw new Error("No JSON found in python output");
      }
      
      const cleanJsonStr = outputData.substring(jsonStart, jsonEnd + 1);
      const parsedOutput = JSON.parse(cleanJsonStr);
      res.json(parsedOutput);
    } catch (e) {
      console.error("Failed to parse python output", e);
      console.error("Raw output", outputData);
      res.status(500).json({ error: "Invalid diagnosis response.", raw: outputData });
    }
  });

  // Write JSON to python stdin
  const inputPayload = JSON.stringify({
    patient_id: patient_id || "GUEST",
    symptoms: symptoms
  });
  
  pythonProcess.stdin.write(inputPayload);
  pythonProcess.stdin.end();
});

// Helper: spawn db_bridge.py (lightweight, no AI imports)
function spawnDbBridge(payload, res, parseMode = 'array') {
  const scriptPath = path.join(__dirname, '../db_bridge.py');
  const pythonExe = process.env.PYTHON_PATH || 'python';
  const proc = spawn(pythonExe, [scriptPath], {
    cwd: path.join(__dirname, '../'),
    env: { ...process.env },
  });
  let out = '';
  proc.stdout.on('data', d => { out += d.toString(); });
  proc.stderr.on('data', () => {});
  proc.on('close', () => {
    try {
      if (parseMode === 'array') {
        const s = out.indexOf('['), e = out.lastIndexOf(']');
        if (s === -1 || e === -1) return res.json([]);
        res.json(JSON.parse(out.substring(s, e + 1)));
      } else {
        const s = out.indexOf('{'), e = out.lastIndexOf('}');
        if (s === -1 || e === -1) return res.json({});
        res.json(JSON.parse(out.substring(s, e + 1)));
      }
    } catch { res.json(parseMode === 'array' ? [] : {}); }
  });
  proc.stdin.write(JSON.stringify(payload));
  proc.stdin.end();
}

// Get History Summary
app.get('/api/history/:patient_id', (req, res) => {
  spawnDbBridge({ action: 'history_summary', patient_id: req.params.patient_id }, res, 'object');
});

// Get recent history
app.get('/api/history/:patient_id/recent', (req, res) => {
  spawnDbBridge({ action: 'history_recent', patient_id: req.params.patient_id }, res, 'array');
});

// Get reports for a patient
app.get('/api/reports/:patient_id', (req, res) => {
  spawnDbBridge({ action: 'get_reports', patient_id: req.params.patient_id }, res, 'array');
});

app.listen(PORT, () => {
   console.log(`Server running on http://localhost:${PORT}`);
});
