import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [siteConfig, setSiteConfig] = useState({
    siteName: '',
    siteDescription: '',
    themeType: 'blog',
    mainSections: ['About', 'Blog']
  });
  
  const [currentSite, setCurrentSite] = useState(null);
  const [generatedContent, setGeneratedContent] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isCreatingSite, setIsCreatingSite] = useState(false);
  
  const [contentForm, setContentForm] = useState({
    contentType: 'Blog Post',
    title: '',
    requirements: '',
    tone: 'Professional'
  });

  const createSite = async () => {
    if (!siteConfig.siteName || !siteConfig.siteDescription) {
      alert('Please fill in site name and description');
      return;
    }

    setIsCreatingSite(true);
    try {
      const response = await axios.post('/api/sites', siteConfig);
      setCurrentSite(response.data);
      alert('✅ Site created successfully!');
    } catch (error) {
      alert('❌ Error creating site: ' + error.message);
    }
    setIsCreatingSite(false);
  };

  const generateContent = async () => {
    if (!currentSite) {
      alert('Please create a site first');
      return;
    }
    
    if (!contentForm.title || !contentForm.requirements) {
      alert('Please fill in title and requirements');
      return;
    }

    setIsGenerating(true);
    try {
      const response = await axios.post('/api/generate-content', {
        siteId: currentSite.site_id,
        ...contentForm,
        siteConfig
      });
      
      setGeneratedContent([...generatedContent, response.data]);
      setContentForm({ ...contentForm, title: '', requirements: '' });
      alert('✅ Content generated successfully!');
    } catch (error) {
      alert('❌ Error generating content: ' + error.message);
    }
    setIsGenerating(false);
  };

  const downloadSite = async () => {
    if (!currentSite) return;
    
    try {
      const response = await axios.get(`/api/sites/${currentSite.site_id}/download`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${siteConfig.siteName.replace(/\s+/g, '-')}-hugo-site.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      alert('❌ Download failed: ' + error.message);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 text-center">
        <h1 className="text-4xl font-bold mb-2">🚀 Hugo AI Studio</h1>
        <p className="text-xl">Create beautiful websites with AI - All in one page!</p>
      </div>

      <div className="container mx-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Site Configuration */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-4 text-gray-800">📝 Site Configuration</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">🏷️ Site Name</label>
                <input
                  type="text"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Tech Innovation Blog"
                  value={siteConfig.siteName}
                  onChange={(e) => setSiteConfig({...siteConfig, siteName: e.target.value})}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">📝 Site Description</label>
                <textarea
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows="3"
                  placeholder="Describe your website..."
                  value={siteConfig.siteDescription}
                  onChange={(e) => setSiteConfig({...siteConfig, siteDescription: e.target.value})}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">🎨 Theme Type</label>
                <select
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  value={siteConfig.themeType}
                  onChange={(e) => setSiteConfig({...siteConfig, themeType: e.target.value})}
                >
                  <option value="blog">Blog</option>
                  <option value="portfolio">Portfolio</option>
                  <option value="business">Business</option>
                  <option value="documentation">Documentation</option>
                </select>
              </div>
              
              <button
                onClick={createSite}
                disabled={isCreatingSite}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-6 rounded-lg font-bold hover:from-blue-700 hover:to-purple-700 disabled:opacity-50"
              >
                {isCreatingSite ? '⏳ Creating...' : '🚀 Create Website'}
              </button>
              
              {currentSite && (
                <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
                  ✅ Site created: <strong>{siteConfig.siteName}</strong>
                </div>
              )}
            </div>
          </div>

          {/* Content Generation */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-4 text-gray-800">🤖 Content Generation</h2>
            
            {!currentSite ? (
              <div className="text-center text-gray-500 py-8">
                <p>👈 Create a website first!</p>
                <p className="text-sm mt-2">Fill out the configuration and click "Create Website"</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">📝 Content Type</label>
                  <select
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    value={contentForm.contentType}
                    onChange={(e) => setContentForm({...contentForm, contentType: e.target.value})}
                  >
                    <option value="Blog Post">Blog Post</option>
                    <option value="About Page">About Page</option>
                    <option value="Contact Page">Contact Page</option>
                    <option value="Service Page">Service Page</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">🏷️ Title</label>
                  <input
                    type="text"
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., Welcome to My Blog"
                    value={contentForm.title}
                    onChange={(e) => setContentForm({...contentForm, title: e.target.value})}
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">📋 Content Requirements</label>
                  <textarea
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    rows="4"
                    placeholder="Describe what you want the AI to write..."
                    value={contentForm.requirements}
                    onChange={(e) => setContentForm({...contentForm, requirements: e.target.value})}
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">🎭 Tone</label>
                  <select
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    value={contentForm.tone}
                    onChange={(e) => setContentForm({...contentForm, tone: e.target.value})}
                  >
                    <option value="Professional">Professional</option>
                    <option value="Casual">Casual</option>
                    <option value="Friendly">Friendly</option>
                    <option value="Formal">Formal</option>
                  </select>
                </div>
                
                <button
                  onClick={generateContent}
                  disabled={isGenerating}
                  className="w-full bg-gradient-to-r from-green-600 to-blue-600 text-white py-3 px-6 rounded-lg font-bold hover:from-green-700 hover:to-blue-700 disabled:opacity-50"
                >
                  {isGenerating ? '🤖 Generating...' : '🚀 Generate Content'}
                </button>
              </div>
            )}
          </div>

          {/* Preview & Download */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-4 text-gray-800">🌐 Preview & Download</h2>
            
            {!currentSite ? (
              <div className="text-center text-gray-500 py-8">
                <p>👈 Create a website to see preview!</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="bg-blue-100 border border-blue-400 text-blue-700 px-4 py-3 rounded">
                  🎉 <strong>{siteConfig.siteName}</strong> is live!
                </div>
                
                <div className="grid grid-cols-2 gap-2">
                  <a
                    href={`http://43.192.149.110:8080/sites/${currentSite.site_id}/`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-blue-600 text-white py-2 px-4 rounded-lg text-center hover:bg-blue-700"
                  >
                    🌐 Open Site
                  </a>
                  <button
                    onClick={downloadSite}
                    className="bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700"
                  >
                    📥 Download
                  </button>
                </div>
                
                <div className="bg-gray-100 p-3 rounded">
                  <p className="text-sm text-gray-600">📄 Content Pages: {generatedContent.length}</p>
                </div>
                
                {generatedContent.length > 0 && (
                  <div>
                    <h3 className="font-bold mb-2">📝 Generated Content</h3>
                    <div className="space-y-2 max-h-60 overflow-y-auto">
                      {generatedContent.map((content, index) => (
                        <div key={index} className="bg-gray-50 p-3 rounded border">
                          <p className="font-medium">{content.title}</p>
                          <p className="text-sm text-gray-600">{content.contentType}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {currentSite && (
                  <div>
                    <h3 className="font-bold mb-2">🖥️ Live Preview</h3>
                    <iframe
                      src={`http://43.192.149.110:8080/sites/${currentSite.site_id}/`}
                      className="w-full h-64 border rounded"
                      title="Site Preview"
                    />
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
