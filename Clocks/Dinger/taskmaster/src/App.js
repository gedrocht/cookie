// src/App.js
import React, { useState, useEffect } from 'react';
import { Button, TextField, List, ListItem, ListItemText, IconButton, Typography, Checkbox } from '@mui/material';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import DeleteIcon from '@mui/icons-material/Delete';
import axios from 'axios';
import { get_payday } from "./Payday.js"

const PAYCHECK = false;

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
});

function App() {
  const [name, setName] = useState('');
  const [responseMessage, setResponseMessage] = useState('');
  const [reminders, setReminders] = useState([]);
  const [newReminder, setNewReminder] = useState('');
  const [currentTime, setCurrentTime] = useState(new Date());
  const [numShots, setNumShots] = useState(0);
  const [lastShot, setLastShot] = useState("");
  const [nextPayday, setNextPayday] = useState("Next paycheck will be"); 
  const [lastMeetingEndTime, setLastMeetingEndTimeRemaining] = useState("");

  useEffect(() => {
    fetchValidReminders();
    fetchNumShots();
    fetchLastShot();
    if (PAYCHECK) {
      setNextPayday(get_payday());
      const update_payday_interval = setInterval(() => setNextPayday(get_payday()), 600000); //600k ms (10 minutes)
    }
    const update_time_interval = setInterval(() => setCurrentTime(new Date()), 1000);
    //const update_last_meeting_end_time_interval = setInterval(()=>{updateLastMeetingTimeRemaining(reminders)}, 600); //60k ms (1 minute)
    setInterval(fetchValidReminders, 60000); //60k ms (1 minute)
    // return () => clearInterval(interval); //???
  }, []);

  const fetchReminders = async () => {
    try {
      const response = await axios.get('http://192.168.0.133:5000/api/reminders');
      setReminders(response.data); 
      updateLastMeetingTimeRemaining(response.data);
      console.log(response);
    } catch (error) {
      console.error('Error fetching reminders:', error);
    }
  };

  const fetchValidReminders = async () => {
    try {
      const response = await axios.get('http://192.168.0.133:5000/api/reminders/valid');
      setReminders(response.data);
      updateLastMeetingTimeRemaining(response.data);
    } catch (error) {
      console.error('Error fetching valid reminders:', error);
    }
  };

  const addReminder = async () => {
    try {
      await axios.post('http://192.168.0.133:5000/api/reminders', { reminder: newReminder });
      fetchValidReminders();
      setNewReminder('');
    } catch (error) {
      console.error('Error adding reminder:', error);
    }
  };

  const deleteReminder = async (id) => {
    try {
      await axios.delete('http://192.168.0.133:5000/api/reminders', { data: { id } });
      fetchValidReminders();
    } catch (error) {
      console.error('Error deleting reminder:', error);
    }
  };

  const completeReminder = async (ID) => {
    try {
      await axios.post('http://192.168.0.133:5000/api/reminders/complete', {ID});
      fetchValidReminders();
    } catch (error) {
      console.error("Error completing reminder:", error);
    }
  };

  const skipReminder = async (ID) => {
    try {
      await axios.post('http://192.168.0.133:5000/api/reminders/skip', {ID});
      fetchValidReminders();
    } catch (error) {
      console.error("Error completing reminder:", error);
    }
  };

  const addDelayReminder = async (ID) => {
    try {
      await axios.post('http://192.168.0.133:5000/api/reminders/add_delay', {ID});
      fetchValidReminders();
    } catch (error) {
      console.error("Error adding to reminder delay:", error);
    }
  };

  const subtractDelayReminder = async (ID) => {
    try {
      await axios.post('http://192.168.0.133:5000/api/reminders/subtract_delay', {ID});
      fetchValidReminders();
    } catch (error) {
      console.error("Error subtracting from reminder delay:", error);
    }
  };

  const sendMessage = async () => {
    try {
      const response = await axios.post('http://192.168.0.133:5000/api/message', { name });
      setResponseMessage(response.data.message);
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const addShot = async () => {
    try {
      const response = await axios.post("http://192.168.0.133:5000/api/shots");
      fetchNumShots();
      fetchLastShot();
    } catch (error) {
      console.error("Error logging shot:", error);
    }
  }

  const fetchNumShots = async () => {
    try {
      const response = await axios.get('http://192.168.0.133:5000/api/shots');
      setNumShots(response.data);
      console.log(response);
    } catch (error) {
      console.error('Error fetching valid reminders:', error);
    }
  }

  const fetchLastShot = async () => {
    try {
      const response = await axios.get('http://192.168.0.133:5000/api/shots/last');
      setLastShot(response.data);
      console.log(response);
    } catch (error) {
      console.error("Error fetching last shot");
    }
  }

  const resetShots = async () => {
    try {
      const response = await axios.post("http://192.168.0.133:5000/api/shots/reset");
      fetchNumShots();
      fetchLastShot();
      console.log(response);
    } catch (error) {
      console.error("Error resetting shots taken:", error);
    }
  }

  const getReminderLength = (reminder) => {
    const _FLAG_LENGTH_FIVE_MINUTES = 8;
    const _FLAG_LENGTH_QUARTER_HOUR = 16;
    const _FLAG_LENGTH_HALF_HOUR = 32;
    const _FLAG_LENGTH_HOUR = 64;
    const _FLAG_LENGTH_HOUR_AND_A_HALF= 128;
    const _FLAG_LENGTH_MULTIPLE_HOURS= 256;
    
    if (reminder.FLAGS & _FLAG_LENGTH_FIVE_MINUTES) return 5;
    if (reminder.FLAGS & _FLAG_LENGTH_QUARTER_HOUR) return 15;
    if (reminder.FLAGS & _FLAG_LENGTH_HALF_HOUR) return 30;
    if (reminder.FLAGS & _FLAG_LENGTH_HOUR) return 60;
    if (reminder.FLAGS & _FLAG_LENGTH_HOUR_AND_A_HALF) return 90;
    if (reminder.FLAGS & _FLAG_LENGTH_MULTIPLE_HOURS) return 200;
    throw new Error("Unrecognized or unassigned reminder length", reminder);
  }

  const updateLastMeetingTimeRemaining = (reminders) => {
    const _T2FLAG_MEETING = 1;
    for (let i = reminders.length - 1; i > -1; i--) {
      let current = reminders[i];
      if (current.T2FLAGS & _T2FLAG_MEETING) {
        let hours = current.hour;
        let minutes = current.minute;
        minutes += getReminderLength(current);
        while (minutes >= 60) {
          minutes -= 60;
          hours++;
        }
        if (hours > 23) {
          hours = 23;
        }
        let now = new Date();
        let now_dayMinutes = now.getHours() * 60 + now.getMinutes();
        let ending_dayMinutes = hours * 60 + minutes;
        // return ending_dayMinutes - now_dayMinutes;
        let diff_minutes = ending_dayMinutes - now_dayMinutes;
        if (diff_minutes < 0) {
          setLastMeetingEndTimeRemaining("00:00");
          return;
        }
        let diff_hours = 0;
        while (diff_minutes >= 60) {
          diff_hours++;
          diff_minutes -= 60;
        }
        setLastMeetingEndTimeRemaining(`${diff_hours < 10?"0":""}${diff_hours}:${diff_minutes < 10?"0":""}${diff_minutes}`);
        return;
      }
    }
    setLastMeetingEndTimeRemaining("");
  }

  function timeSince(dateString) {
    const timestamp = new Date(dateString);
    const now = new Date();
    const secondsPast = (now.getTime() - timestamp.getTime()) / 1000;
    let day, month, year;

    if (secondsPast < 60) {
        return parseInt(secondsPast) + ' seconds ago';
    }
    if (secondsPast < 3600) {
        return parseInt(secondsPast / 60) + ' minutes ago';
    }
    if (secondsPast <= 86400) {
        return parseInt(secondsPast / 3600) + ' hours ago';
    }
    if (secondsPast > 86400) {
        day = timestamp.getDate();
        month = timestamp.toDateString().match(/ [a-zA-Z]*/)[0].replace(" ", "");
        year = timestamp.getFullYear() == now.getFullYear() ? "" : " " + timestamp.getFullYear();
        return day + " " + month + year;
    }
}

  return (
    <ThemeProvider theme={darkTheme}>
      <div style={{ margin: '20px' }}>
        <Typography variant="h5" style={{ marginBottom: "20px", display: PAYCHECK?"block":"none" }}>
          {nextPayday}
        </Typography>
        <span style={{display: "none"}}>
          <Typography variant="h5" style={{ marginBottom: '20px' }}>
            Current Time: {currentTime.toLocaleTimeString()}
          </Typography>
          <div>
            <input 
              type="text" 
              placeholder="Enter your name" 
              value={name} 
              onChange={e => setName(e.target.value)} 
            />
            <button onClick={sendMessage}>Send</button>
            {responseMessage && <p>{responseMessage}</p>}
          </div>

          <input 
            type="text" 
            value={newReminder} 
            onChange={(e) => setNewReminder(e.target.value)}
            style={{ marginRight: '10px' }}
          />
          <Button variant="contained" color="primary" onClick={addReminder}>
            Add Reminder
          </Button>
        </span>
        <Typography variant="h5" style={{display: numShots > 0 ? "" : "none", marginBottom: '10px' }}>
          {numShots} Shot{numShots===1?"":"s"} Taken
        </Typography>
        <Typography variant="h6" style={{display: numShots > 0 ? "" : "none", marginBottom: '20px' }}>
          Last shot: {timeSince(lastShot)}
        </Typography>
        <Button style={{margin: '10px', display: "block"}} variant="contained" color="primary" onClick={addShot}>
          Log Shot
        </Button>
        <Button style={{display: numShots > 0 ? "" : "none", margin: '10px'}} variant="contained" color="secondary" onClick={resetShots}>
          Reset Shot Log
        </Button>
        <Typography style={{display: lastMeetingEndTime === "" ? "none" : "", margin: "10px"}}>
          Last meeting will end in {lastMeetingEndTime}
        </Typography>
        <List>
          {reminders.map((reminder, index) => (
            <ListItem key={index} style={
              {
                borderBottom: "1px solid #ddd", 
                marginTop: '10px', 
                display: (reminder.SKIPPED === "True" || reminder.COMPLETED === "True") ? "none" : "block"
              }}>
              <ListItemText
                primary={<Typography>{reminder.reminder}</Typography>}
                secondary={<Typography>{new Date(0, 0, 0, parseInt(reminder.hour) + parseInt(reminder.DELAY), reminder.minute)
                  .toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })}</Typography>}
              />
              <Typography style={{display: reminder.DELAY === 0 ? "none" : ""}}>(Delayed by {reminder.DELAY} hour{reminder.DELAY===1?"":"s"})</Typography>
              <Button key={`${index}-CompleteButton`} style={{margin: '10px'}} variant="contained" color="primary" onClick={()=>{completeReminder(reminder.ID)}}>Complete</Button>
              <Button key={`${index}-SkipButton`} style={{margin: '10px'}} variant="contained" color="secondary" onClick={()=>{skipReminder(reminder.ID)}}>Skip</Button>
              <Button key={`${index}-AddDelayButton`} style={{display: reminder.FLAGS & 32768 ? "none":"", margin: '10px'}} variant="contained" color="primary" onClick={()=>{addDelayReminder(reminder.ID)}}>Add Delay</Button>
              <Button key={`${index}-SubtractDelayButton`} style={{display: reminder.DELAY===0?"none":"", margin: '10px'}} variant="contained" color="secondary" onClick={()=>{subtractDelayReminder(reminder.ID)}}>Subtract Delay</Button>
            </ListItem>
          ))}
        </List>
        </div>
    </ThemeProvider>
  );
}

/*Object.entries(reminder).map(([key, value]) => (
  <Typography key={`${index}-${key}`}>{`${key}: ${value}`}</Typography>))}
*/

export default App;
