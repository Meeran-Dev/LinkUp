import { createContext, useContext, useEffect, useState, useRef } from 'react';
import { useAuth } from './AuthContext';

const SocketContext = createContext(null);

const SOCKET_URL = 'wss://linkup-43u1.onrender.com';

export function SocketProvider({ children }) {
  const { user } = useAuth();
  const socketRef = useRef(null);
  const [connected, setConnected] = useState(false);
  const [latestEvent, setLatestEvent] = useState(null);

  useEffect(() => {
      if (!user?.user_id) return;

      const socket = new WebSocket(`${SOCKET_URL}/ws/${user.user_id}`);

      socket.onopen = () => {
        setConnected(true);
      };

      socket.onclose = () => {
        setConnected(false);
      };

      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setLatestEvent(data);
      };

      socketRef.current = socket;

    return () => {
      socket.close();
    };
  }, [user?.user_id]);

  const sendMessage = (payload) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(payload));
    }
  };

  return (
    <SocketContext.Provider value={{ connected, latestEvent, sendMessage }}>
      {children}
    </SocketContext.Provider>
  );
}

export function useSocket() {
  const context = useContext(SocketContext);
  if (!context) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  return context;
}