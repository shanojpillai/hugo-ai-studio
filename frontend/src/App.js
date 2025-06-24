import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import toast, { Toaster } from 'react-hot-toast';

const API_BASE = 'http://43.192.149.110:8000';

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: "👋 Hi! I'm your AI website builder. Just tell me what kind of website you want to create and I'll build it for you!\n\nFor example:\n• \"Create a tech blog about AI and machine learning\"\n• \"Build a portfolio website for a photographer\"\n• \"Make a business website for a restaurant\""
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentSite, setCurrentSite] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const addMessage = (type, content) => {
    const newMessage = {
      id: Date.now(),
      type,
      content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newMessage]);
    return newMessage;
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    
    // Add user message
    addMessage('user', userMessage);
    
    // Add loading message
    const loadingMessage = addMessage('bot', '🤖 Creating your website...');
    setIsLoading(true);

    try {
      // Step 1: Create site based on user description
      const siteResponse = await axios.post(`${API_BASE}/api/create-from-description`, {
        description: userMessage
      });

      const site = siteResponse.data;
      setCurrentSite(site);

      // Update loading message with success
      setMessages(prev => prev.map(msg => 
        msg.id === loadingMessage.id 
          ? {
              ...msg,
              content: `✅ **${site.siteName}** created successfully!\n\n🌐 **Preview**: [View your website](http://43.192.149.110:8080/sites/${site.siteId}/)\n\n📥 **Download**: Click the download button below to get your complete website files.`,
              siteId: site.siteId,
              siteName: site.siteName
            }
          : msg
      ));

      toast.success('Website created successfully!');

    } catch (error) {
      console.error('Error creating website:', error);
      
      // Update loading message with error
      setMessages(prev => prev.map(msg => 
        msg.id === loadingMessage.id 
          ? {
              ...msg,
              content: `❌ Sorry, I couldn't create your website. Error: ${error.response?.data?.detail || error.message}\n\nPlease try again with a different description.`
            }
          : msg
      ));

      toast.error('Failed to create website');
    }

    setIsLoading(false);
  };

  const handleDownload = async (siteId, siteName) => {
    try {
      toast.loading('Preparing download...');
      
      const response = await axios.get(`${API_BASE}/api/sites/${siteId}/download`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${siteName.replace(/\s+/g, '-')}-hugo-site.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success('Download started!');
    } catch (error) {
      console.error('Download error:', error);
      toast.error('Download failed');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      <Toaster position="top-right" />
      
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 shadow-lg">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-2">🚀 Hugo AI Studio</h1>
          <p className="text-blue-100">Chat with AI to create your perfect website</p>
        </div>
      </div>

      {/* Chat Container */}
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-white rounded-lg shadow-xl h-[600px] flex flex-col">
          
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-4 ${
                    message.type === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  <div className="whitespace-pre-wrap">{message.content}</div>
                  
                  {/* Download button for bot messages with siteId */}
                  {message.type === 'bot' && message.siteId && (
                    <div className="mt-3 flex gap-2">
                      <a
                        href={`http://43.192.149.110:8080/sites/${message.siteId}/`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 transition-colors"
                      >
                        🌐 Open Website
                      </a>
                      <button
                        onClick={() => handleDownload(message.siteId, message.siteName)}
                        className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-700 transition-colors"
                      >
                        📥 Download ZIP
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t p-4">
            <div className="flex gap-3">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Describe the website you want to create..."
                className="flex-1 border border-gray-300 rounded-lg p-3 resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows="2"
                disabled={isLoading}
              />
              <button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isLoading}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? '⏳' : '🚀'}
              </button>
            </div>
            <p className="text-sm text-gray-500 mt-2">
              Press Enter to send, Shift+Enter for new line
            </p>
          </div>
        </div>

        {/* Examples */}
        <div className="mt-6 bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold mb-3">💡 Example Requests:</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {[
              "Create a tech blog about artificial intelligence and machine learning",
              "Build a portfolio website for a graphic designer",
              "Make a business website for a local restaurant with menu",
              "Create a documentation site for a software project"
            ].map((example, index) => (
              <button
                key={index}
                onClick={() => setInputMessage(example)}
                className="text-left p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors text-sm"
                disabled={isLoading}
              >
                "{example}"
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
