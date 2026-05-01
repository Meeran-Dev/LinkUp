import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import './Chat.css';

export default function Chat() {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('dms');
  const [conversations, setConversations] = useState([]);
  const [groups, setGroups] = useState([]);
  const [selectedChat, setSelectedChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [showCreateGroup, setShowCreateGroup] = useState(false);
  const [newGroupName, setNewGroupName] = useState('');
  const [showAddMember, setShowAddMember] = useState(false);
  const [showNewDm, setShowNewDm] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [groupMembers, setGroupMembers] = useState([]);
  const [onlineUsers, setOnlineUsers] = useState(new Set());
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (user?.user_id) {
      loadConversations();
      loadGroups();
      loadOnlineUsers();
    }
  }, [user?.user_id]);

  // Poll for online users every 10 seconds
  useEffect(() => {
    const interval = setInterval(loadOnlineUsers, 10000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedChat && user?.user_id) {
      loadMessages();
    }
  }, [selectedChat, activeTab, user?.user_id]);

  // Load group members when a group is selected
  useEffect(() => {
    if (activeTab === 'groups' && selectedChat?.id) {
      loadGroupMembers(selectedChat.id);
    } else {
      setGroupMembers([]);
    }
  }, [selectedChat, activeTab]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (searchQuery.length >= 2) {
      searchUsers();
    } else {
      setSearchResults([]);
    }
  }, [searchQuery]);

  const loadGroupMembers = async (groupId) => {
    try {
      const token = localStorage.getItem('token');
      const data = await api.getGroupMembers(groupId, token);
      setGroupMembers(data);
    } catch (err) {
      console.error('Failed to load group members:', err);
    }
  };

  const loadOnlineUsers = async () => {
    try {
      const token = localStorage.getItem('token');
      const online = await api.getOnlineUsers(token);
      setOnlineUsers(online);
    } catch (err) {
      console.error('Failed to load online users:', err);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadConversations = async () => {
    try {
      const token = localStorage.getItem('token');
      const data = await api.getConversations(user.user_id, token);
      
      // Also load pending DMs from localStorage
      const pendingDMs = api.getPendingDMs(user.user_id);
      
      // Merge server conversations with pending DMs
      const merged = [...data];
      pendingDMs.forEach(pending => {
        if (!merged.find(c => c.id === pending.id)) {
          merged.push(pending);
        }
      });
      
      setConversations(merged);
    } catch (err) {
      console.error('Failed to load conversations:', err);
    }
  };

  const loadGroups = async () => {
    try {
      const token = localStorage.getItem('token');
      const data = await api.getGroups(user.user_id, token);
      setGroups(data);
    } catch (err) {
      console.error('Failed to load groups:', err);
    }
  };

  const isGroupCreator = (group) => {
    return group.created_by === user?.user_id;
  };

  const loadMessages = async () => {
    try {
      const token = localStorage.getItem('token');
      if (activeTab === 'dms' && selectedChat) {
        const data = await api.getDirectMessages(user.user_id, selectedChat.id, token);
        setMessages(data);
      } else if (activeTab === 'groups' && selectedChat) {
        const data = await api.getGroupMessages(selectedChat.id, token);
        setMessages(data);
      } else if (activeTab === 'global') {
        const data = await api.getGlobalChat(token);
        setMessages(data);
      }
    } catch (err) {
      console.error('Failed to load messages:', err);
    }
  };

  const searchUsers = async () => {
    try {
      const token = localStorage.getItem('token');
      const data = await api.searchUsers(searchQuery, token);
      setSearchResults(data.filter(u => u.id !== user.user_id));
    } catch (err) {
      console.error('Failed to search users:', err);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedChat) return;

    try {
      const token = localStorage.getItem('token');
      if (activeTab === 'dms') {
        await api.sendDirectMessage(user.user_id, selectedChat.id, newMessage, token);
      } else if (activeTab === 'groups') {
        await api.sendGroupMessage(selectedChat.id, user.user_id, newMessage, token);
      } else if (activeTab === 'global') {
        await api.sendGlobalMessage(user.user_id, newMessage, token);
      }
      setNewMessage('');
      loadMessages();
    } catch (err) {
      console.error('Failed to send message:', err);
    }
  };

  const handleCreateGroup = async (e) => {
    e.preventDefault();
    if (!newGroupName.trim()) return;

    try {
      const token = localStorage.getItem('token');
      await api.createGroup(newGroupName, user.user_id, token);
      setNewGroupName('');
      setShowCreateGroup(false);
      loadGroups();
    } catch (err) {
      console.error('Failed to create group:', err);
    }
  };

  const handleAddMember = async (e) => {
    e.preventDefault();
    if (!selectedUser || !selectedChat) return;

    try {
      const token = localStorage.getItem('token');
      await api.addGroupMember(selectedChat.id, selectedUser.id, user.user_id, token);
      setSelectedUser(null);
      setSearchQuery('');
      setSearchResults([]);
      setShowAddMember(false);
    } catch (err) {
      console.error('Failed to add member:', err);
      alert(err.message || 'Failed to add member');
    }
  };

  const handleStartDm = async (e) => {
    e.preventDefault();
    if (!selectedUser) return;

    const existing = conversations.find(c => c.id === selectedUser.id);
    if (existing) {
      setSelectedChat(existing);
    } else {
      const newConv = { id: selectedUser.id, username: selectedUser.username, last_message: '' };
      setConversations(prev => [...prev, newConv]);
      api.savePendingDM(user.user_id, selectedUser.id, selectedUser.username);
      setSelectedChat(newConv);
    }
    setSelectedUser(null);
    setSearchQuery('');
    setSearchResults([]);
    setShowNewDm(false);
    setActiveTab('dms');
  };

  const handleDeleteGroup = async (e) => {
    e.preventDefault();
    if (!selectedChat || !confirm('Are you sure you want to delete this group?')) return;

    try {
      const token = localStorage.getItem('token');
      await api.deleteGroup(selectedChat.id, user.user_id, token);
      setSelectedChat(null);
      loadGroups();
    } catch (err) {
      console.error('Failed to delete group:', err);
      alert(err.message || 'Failed to delete group');
    }
  };

  const handleRemoveMember = async (memberId) => {
    if (!selectedChat || !confirm('Remove this member from the group?')) return;

    try {
      const token = localStorage.getItem('token');
      await api.removeGroupMember(selectedChat.id, memberId, user.user_id, token);
      loadGroupMembers(selectedChat.id);
    } catch (err) {
      console.error('Failed to remove member:', err);
      alert(err.message || 'Failed to remove member');
    }
  };

  return (
    <div className="chat-container">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h2>LinkUp</h2>
          <button className="logout-btn" onClick={logout}>Logout</button>
        </div>

        <div className="tabs">
          <button 
            className={`tab ${activeTab === 'dms' ? 'active' : ''}`}
            onClick={() => { setActiveTab('dms'); setSelectedChat(null); }}
          >
            DMs
          </button>
          <button 
            className={`tab ${activeTab === 'groups' ? 'active' : ''}`}
            onClick={() => { setActiveTab('groups'); setSelectedChat(null); }}
          >
            Groups
          </button>
          <button 
            className={`tab ${activeTab === 'global' ? 'active' : ''}`}
            onClick={() => { setActiveTab('global'); setSelectedChat(null); }}
          >
            Global
          </button>
        </div>

        <div className="chat-list">
          {activeTab === 'dms' && (
            <>
              <button className="create-group-btn" onClick={() => setShowNewDm(true)}>
                + New DM
              </button>
              {conversations.map((conv) => (
                <div 
                  key={conv.id} 
                  className={`chat-item ${selectedChat?.id === conv.id ? 'active' : ''}`}
                  onClick={() => setSelectedChat(conv)}
                >
                  <div className="avatar">
                    {conv.username?.[0]}
                    <span className={`presence-dot ${onlineUsers.has(conv.id) ? 'online' : 'offline'}`}></span>
                  </div>
                  <div className="chat-info">
                    <div className="chat-name">{conv.username}</div>
                    <div className="last-message">{conv.last_message}</div>
                  </div>
                </div>
              ))}
            </>
          )}

          {activeTab === 'groups' && (
            <>
              <button className="create-group-btn" onClick={() => setShowCreateGroup(true)}>
                + Create Group
              </button>
              {groups.map((group) => (
                <div 
                  key={group.id} 
                  className={`chat-item ${selectedChat?.id === group.id ? 'active' : ''}`}
                  onClick={() => setSelectedChat(group)}
                >
                  <div className="avatar group-avatar">G</div>
                  <div className="chat-info">
                    <div className="chat-name">{group.name}</div>
                  </div>
                </div>
              ))}
            </>
          )}

          {activeTab === 'global' && (
            <div 
              className={`chat-item ${selectedChat === 'global' ? 'active' : ''}`}
              onClick={() => setSelectedChat({ id: 'global', name: 'Global Chat' })}
            >
              <div className="avatar group-avatar">🌍</div>
              <div className="chat-info">
                <div className="chat-name">Global Chat</div>
              </div>
            </div>
          )}
        </div>

        <div className="user-info">
          <div className="user-avatar">{user?.username?.[0]?.toUpperCase()}</div>
          <div className="user-name">{user?.username}</div>
        </div>
      </aside>

      <main className="chat-main">
        {selectedChat ? (
          <>
            <div className="chat-header">
              <div className="chat-title">{selectedChat.name}</div>
              {activeTab === 'groups' && isGroupCreator(selectedChat) && (
                <div className="group-actions">
                  <button className="add-member-btn" onClick={() => setShowAddMember(true)}>
                    + Add Member
                  </button>
                  <button className="delete-group-btn" onClick={handleDeleteGroup}>
                    Delete Group
                  </button>
                </div>
              )}
            </div>

            <div className="messages-container">
              {messages.length === 0 ? (
                <div className="no-messages">No messages yet. Start the conversation!</div>
              ) : (
                messages.map((msg, index) => (
                  <div 
                    key={index} 
                    className={`message ${msg.sender_id === user?.user_id ? 'own' : ''}`}
                  >
                    {activeTab !== 'global' && (
                      <div className="message-sender">
                        {msg.sender_name || msg.sender_username || 'User'}
                      </div>
                    )}
                    <div className="message-content">{msg.content}</div>
                    <div className="message-time">
                      {msg.created_at ? new Date(msg.created_at).toLocaleTimeString() : ''}
                    </div>
                  </div>
                ))
              )}
              <div ref={messagesEndRef} />
            </div>

            <form className="message-form" onSubmit={handleSendMessage}>
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Type a message..."
              />
              <button type="submit">Send</button>
            </form>
          </>
        ) : (
          <div className="no-chat-selected">
            <h3>Welcome to LinkUp!</h3>
            <p>Select a conversation to start chatting</p>
          </div>
        )}
      </main>

      {activeTab === 'groups' && selectedChat && (
        <aside className="members-sidebar">
          <div className="members-header">
            <h3>Members ({groupMembers.length})</h3>
          </div>
          <div className="members-list">
            {groupMembers.map((member) => (
              <div key={member.id} className="member-item">
                <div className="member-avatar">
                  {member.username?.[0]?.toUpperCase() || '?'}
                  <span className={`presence-dot ${onlineUsers.has(member.id) ? 'online' : 'offline'}`}></span>
                </div>
                <div className="member-name">
                  {member.username}
                  {member.is_admin && <span className="admin-tag">Admin</span>}
                </div>
                {isGroupCreator(selectedChat) && member.id !== user?.user_id && (
                  <button 
                    className="remove-member-btn"
                    onClick={() => handleRemoveMember(member.id)}
                    title="Remove member"
                  >
                    ×
                  </button>
                )}
              </div>
            ))}
          </div>
        </aside>
      )}

      {showCreateGroup && (
        <div className="modal-overlay" onClick={() => setShowCreateGroup(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Create New Group</h3>
            <form onSubmit={handleCreateGroup}>
              <input
                type="text"
                value={newGroupName}
                onChange={(e) => setNewGroupName(e.target.value)}
                placeholder="Group name"
                required
              />
              <div className="modal-actions">
                <button type="button" onClick={() => setShowCreateGroup(false)}>
                  Cancel
                </button>
                <button type="submit">Create</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showAddMember && (
        <div className="modal-overlay" onClick={() => setShowAddMember(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Add Member to Group</h3>
            <form onSubmit={handleAddMember}>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by username or email..."
                autoFocus
              />
              {searchResults.length > 0 && (
                <div className="search-results">
                  {searchResults.map((u) => (
                    <div 
                      key={u.id} 
                      className={`search-result ${selectedUser?.id === u.id ? 'selected' : ''}`}
                      onClick={() => setSelectedUser(u)}
                    >
                      <div className="result-name">{u.username}</div>
                      <div className="result-email">{u.email}</div>
                    </div>
                  ))}
                </div>
              )}
              <div className="modal-actions">
                <button type="button" onClick={() => { setShowAddMember(false); setSelectedUser(null); setSearchQuery(''); }}>
                  Cancel
                </button>
                <button type="submit" disabled={!selectedUser}>Add</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showNewDm && (
        <div className="modal-overlay" onClick={() => setShowNewDm(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Start New DM</h3>
            <form onSubmit={handleStartDm}>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by username or email..."
                autoFocus
              />
              {searchResults.length > 0 && (
                <div className="search-results">
                  {searchResults.map((u) => (
                    <div 
                      key={u.id} 
                      className={`search-result ${selectedUser?.id === u.id ? 'selected' : ''}`}
                      onClick={() => setSelectedUser(u)}
                    >
                      <div className="result-name">{u.username}</div>
                      <div className="result-email">{u.email}</div>
                    </div>
                  ))}
                </div>
              )}
              <div className="modal-actions">
                <button type="button" onClick={() => { setShowNewDm(false); setSelectedUser(null); setSearchQuery(''); }}>
                  Cancel
                </button>
                <button type="submit" disabled={!selectedUser}>Start DM</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}