import React, { useState, useEffect } from 'react';
import { PlusCircle, Edit3, Trash2, Send, Image, Video, Calendar, BarChart3, Settings } from 'lucide-react';

// Mock data for development
const mockPosts = [
  {
    id: 1,
    content: "Check out our new product launch! 🚀 #innovation #tech",
    platforms: ['facebook', 'linkedin', 'twitter'],
    status: 'published',
    scheduledDate: '2025-07-10T10:00:00Z',
    analytics: { likes: 45, shares: 12, comments: 8 }
  },
  {
    id: 2,
    content: "Behind the scenes at our office today 📸",
    platforms: ['instagram', 'facebook'],
    status: 'draft',
    scheduledDate: null,
    analytics: { likes: 0, shares: 0, comments: 0 }
  }
];

const platformColors = {
  facebook: 'bg-blue-500',
  instagram: 'bg-pink-500',
  linkedin: 'bg-blue-700',
  twitter: 'bg-sky-400'
};

const SocialMediaManager = () => {
  const [posts, setPosts] = useState(mockPosts);
  const [activeTab, setActiveTab] = useState('create');
  const [selectedPost, setSelectedPost] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    content: '',
    platforms: [],
    scheduledDate: '',
    mediaFiles: []
  });

  const handleCreatePost = () => {
    setSelectedPost(null);
    setFormData({
      content: '',
      platforms: [],
      scheduledDate: '',
      mediaFiles: []
    });
    setIsModalOpen(true);
  };

  const handleEditPost = (post) => {
    setSelectedPost(post);
    setFormData({
      content: post.content,
      platforms: post.platforms,
      scheduledDate: post.scheduledDate || '',
      mediaFiles: []
    });
    setIsModalOpen(true);
  };

  const handleDeletePost = (postId) => {
    if (window.confirm('Are you sure you want to delete this post?')) {
      setPosts(posts.filter(post => post.id !== postId));
    }
  };

  const handleSavePost = () => {
    const newPost = {
      id: selectedPost ? selectedPost.id : Date.now(),
      content: formData.content,
      platforms: formData.platforms,
      status: formData.scheduledDate ? 'scheduled' : 'draft',
      scheduledDate: formData.scheduledDate || null,
      analytics: selectedPost ? selectedPost.analytics : { likes: 0, shares: 0, comments: 0 }
    };

    if (selectedPost) {
      setPosts(posts.map(post => post.id === selectedPost.id ? newPost : post));
    } else {
      setPosts([...posts, newPost]);
    }

    setIsModalOpen(false);
  };

  const handlePlatformToggle = (platform) => {
    setFormData(prev => ({
      ...prev,
      platforms: prev.platforms.includes(platform)
        ? prev.platforms.filter(p => p !== platform)
        : [...prev.platforms, platform]
    }));
  };

  const PostCard = ({ post }) => (
    <div className="bg-white rounded-lg shadow-md p-6 mb-4 border border-gray-200">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <p className="text-gray-800 mb-3">{post.content}</p>
          <div className="flex flex-wrap gap-2 mb-3">
            {post.platforms.map(platform => (
              <span
                key={platform}
                className={`px-3 py-1 rounded-full text-white text-sm ${platformColors[platform]}`}
              >
                {platform}
              </span>
            ))}
          </div>
          <div className="flex items-center gap-4 text-sm text-gray-600">
            <span className={`px-2 py-1 rounded-full text-xs ${
              post.status === 'published' ? 'bg-green-100 text-green-800' :
              post.status === 'scheduled' ? 'bg-yellow-100 text-yellow-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {post.status}
            </span>
            {post.scheduledDate && (
              <span>{new Date(post.scheduledDate).toLocaleString()}</span>
            )}
          </div>
        </div>
        <div className="flex gap-2 ml-4">
          <button
            onClick={() => handleEditPost(post)}
            className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded"
          >
            <Edit3 size={16} />
          </button>
          <button
            onClick={() => handleDeletePost(post.id)}
            className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded"
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>
      {post.status === 'published' && (
        <div className="flex gap-4 pt-3 border-t border-gray-200 text-sm text-gray-600">
          <span>👍 {post.analytics.likes}</span>
          <span>🔄 {post.analytics.shares}</span>
          <span>💬 {post.analytics.comments}</span>
        </div>
      )}
    </div>
  );

  const CreatePostModal = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-4">
          {selectedPost ? 'Edit Post' : 'Create New Post'}
        </h2>
        
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Content</label>
          <textarea
            value={formData.content}
            onChange={(e) => setFormData({...formData, content: e.target.value})}
            className="w-full p-3 border border-gray-300 rounded-lg resize-none"
            rows="4"
            placeholder="What's on your mind?"
          />
          <div className="text-sm text-gray-500 mt-1">
            {formData.content.length}/2200 characters
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Platforms</label>
          <div className="grid grid-cols-2 gap-2">
            {['facebook', 'instagram', 'linkedin', 'twitter'].map(platform => (
              <label key={platform} className="flex items-center gap-2 p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                <input
                  type="checkbox"
                  checked={formData.platforms.includes(platform)}
                  onChange={() => handlePlatformToggle(platform)}
                  className="rounded"
                />
                <span className="capitalize">{platform}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Schedule (Optional)</label>
          <input
            type="datetime-local"
            value={formData.scheduledDate}
            onChange={(e) => setFormData({...formData, scheduledDate: e.target.value})}
            className="w-full p-3 border border-gray-300 rounded-lg"
          />
        </div>

        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">Media</label>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <div className="flex justify-center gap-4 mb-2">
              <Image className="text-gray-400" size={24} />
              <Video className="text-gray-400" size={24} />
            </div>
            <p className="text-gray-600">Drop files here or click to upload</p>
            <p className="text-sm text-gray-500 mt-1">Images, videos, GIFs supported</p>
          </div>
        </div>

        <div className="flex gap-3 justify-end">
          <button
            onClick={() => setIsModalOpen(false)}
            className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={handleSavePost}
            disabled={!formData.content.trim() || formData.platforms.length === 0}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {selectedPost ? 'Update' : 'Save'} Post
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <h1 className="text-2xl font-bold text-gray-900">Social Media Manager</h1>
            <button
              onClick={handleCreatePost}
              className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              <PlusCircle size={20} />
              Create Post
            </button>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {[
              { id: 'create', label: 'Posts', icon: Edit3 },
              { id: 'schedule', label: 'Schedule', icon: Calendar },
              { id: 'analytics', label: 'Analytics', icon: BarChart3 },
              { id: 'settings', label: 'Settings', icon: Settings }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 py-4 px-2 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <tab.icon size={16} />
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'create' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">Your Posts</h2>
              <div className="flex gap-2">
                <select className="px-3 py-2 border border-gray-300 rounded-lg">
                  <option>All Platforms</option>
                  <option>Facebook</option>
                  <option>Instagram</option>
                  <option>LinkedIn</option>
                  <option>Twitter</option>
                </select>
                <select className="px-3 py-2 border border-gray-300 rounded-lg">
                  <option>All Status</option>
                  <option>Published</option>
                  <option>Scheduled</option>
                  <option>Draft</option>
                </select>
              </div>
            </div>
            
            <div className="grid gap-4">
              {posts.map(post => (
                <PostCard key={post.id} post={post} />
              ))}
            </div>
          </div>
        )}

        {activeTab === 'schedule' && (
          <div className="text-center py-12">
            <Calendar className="mx-auto mb-4 text-gray-400" size={48} />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Schedule View</h3>
            <p className="text-gray-600">Calendar view for scheduled posts will be implemented here</p>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="text-center py-12">
            <BarChart3 className="mx-auto mb-4 text-gray-400" size={48} />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Analytics Dashboard</h3>
            <p className="text-gray-600">Performance metrics and insights will be displayed here</p>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="text-center py-12">
            <Settings className="mx-auto mb-4 text-gray-400" size={48} />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Settings</h3>
            <p className="text-gray-600">Platform connections and preferences will be managed here</p>
          </div>
        )}
      </main>

      {/* Modal */}
      {isModalOpen && <CreatePostModal />}
    </div>
  );
};

export default SocialMediaManager;
