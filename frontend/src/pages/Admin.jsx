import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '../components/ui/dialog';
import { 
  ArrowLeft, Users, Package, Rocket, BarChart3, 
  Search, RefreshCw, Loader2, Shield, Bot, Send,
  Crown, ChevronRight, Plus, Trash2, Edit, Clock, Play
} from 'lucide-react';
import { toast } from 'sonner';
import { 
  getAdminStats, getAdminUsers, updateUserTier, getRecentActivity,
  createAdminUser, deleteAdminUser, updateAdminUser, getSchedulerStatus, triggerDailyReports
} from '../lib/api';

export default function Admin() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [totalUsers, setTotalUsers] = useState(0);
  const [recentActivity, setRecentActivity] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [updatingTier, setUpdatingTier] = useState(null);
  const [schedulerStatus, setSchedulerStatus] = useState(null);
  const [triggeringReports, setTriggeringReports] = useState(false);
  
  // Modal states
  const [showAddUser, setShowAddUser] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(null);
  const [addingUser, setAddingUser] = useState(false);
  const [deletingUser, setDeletingUser] = useState(false);
  const [newUser, setNewUser] = useState({ email: '', name: '', password: '', subscription_tier: 'free' });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [statsRes, usersRes, activityRes, schedulerRes] = await Promise.all([
        getAdminStats(),
        getAdminUsers(0, 50),
        getRecentActivity(10),
        getSchedulerStatus().catch(() => ({ data: null }))
      ]);
      setStats(statsRes.data);
      setUsers(usersRes.data.users);
      setTotalUsers(usersRes.data.total);
      setRecentActivity(activityRes.data);
      setSchedulerStatus(schedulerRes.data);
    } catch (error) {
      if (error.response?.status === 403) {
        toast.error('Admin access required');
        navigate('/dashboard');
      } else {
        toast.error('Failed to load admin data');
      }
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    if (!user?.is_admin) {
      navigate('/dashboard');
      return;
    }
    fetchData();
  }, [user, navigate, fetchData]);

  const handleUpdateTier = async (userId, newTier) => {
    setUpdatingTier(userId);
    try {
      await updateUserTier(userId, newTier);
      toast.success('User tier updated');
      fetchData();
    } catch (error) {
      toast.error('Failed to update tier');
    } finally {
      setUpdatingTier(null);
    }
  };

  const handleAddUser = async () => {
    if (!newUser.email || !newUser.name || !newUser.password) {
      toast.error('All fields required');
      return;
    }
    setAddingUser(true);
    try {
      await createAdminUser(newUser);
      toast.success('User created');
      setShowAddUser(false);
      setNewUser({ email: '', name: '', password: '', subscription_tier: 'free' });
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create user');
    } finally {
      setAddingUser(false);
    }
  };

  const handleDeleteUser = async (userId) => {
    setDeletingUser(true);
    try {
      await deleteAdminUser(userId);
      toast.success('User deleted');
      setShowDeleteConfirm(null);
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete user');
    } finally {
      setDeletingUser(false);
    }
  };

  const handleTriggerReports = async () => {
    setTriggeringReports(true);
    try {
      await triggerDailyReports();
      toast.success('Daily reports triggered!');
    } catch (error) {
      toast.error('Failed to trigger reports');
    } finally {
      setTriggeringReports(false);
    }
  };

  const filteredUsers = users.filter(u => 
    u.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.email?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const tiers = ['free', 'sniper', 'elite', 'agency', 'enterprise'];

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0A0A0A] flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0A0A0A]">
      {/* Header */}
      <header className="border-b border-white/5 bg-[#0A0A0A]/80 backdrop-blur sticky top-0 z-50">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-4">
            <Button 
              variant="ghost" 
              onClick={() => navigate('/dashboard')}
              className="text-muted-foreground hover:text-white"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Dashboard
            </Button>
            <Badge className="bg-primary/20 text-primary">
              <Shield className="w-3 h-3 mr-1" />
              Admin Panel
            </Badge>
          </div>
          <Button 
            variant="outline" 
            className="border-white/10"
            onClick={fetchData}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </header>

      <main className="p-6 max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Admin Dashboard</h1>

        {/* Scheduler Status */}
        <Card className="bg-[#121212] border-white/5 mb-8">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className={`w-10 h-10 rounded-lg ${schedulerStatus?.running ? 'bg-green-500/10' : 'bg-red-500/10'} flex items-center justify-center`}>
                  <Clock className={`w-5 h-5 ${schedulerStatus?.running ? 'text-green-500' : 'text-red-500'}`} />
                </div>
                <div>
                  <p className="font-medium">Background Scheduler</p>
                  <p className="text-xs text-muted-foreground">
                    {schedulerStatus?.running ? 'Running - Daily reports at 7 AM Eastern' : 'Not running'}
                  </p>
                </div>
              </div>
              <Button
                onClick={handleTriggerReports}
                disabled={triggeringReports}
                variant="outline"
                className="border-primary/30 text-primary"
              >
                {triggeringReports ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Play className="w-4 h-4 mr-2" />}
                Send Reports Now
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Stats Overview */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4 mb-8">
            <Card className="bg-[#121212] border-white/5">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    <Users className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{stats.total_users}</p>
                    <p className="text-xs text-muted-foreground">Total Users</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-[#121212] border-white/5">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-yellow-500/10 flex items-center justify-center">
                    <Crown className="w-5 h-5 text-yellow-500" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{stats.paid_users}</p>
                    <p className="text-xs text-muted-foreground">Paid Users</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-[#121212] border-white/5">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                    <Bot className="w-5 h-5 text-green-500" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{stats.users_with_openai}</p>
                    <p className="text-xs text-muted-foreground">With OpenAI</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-[#121212] border-white/5">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                    <Send className="w-5 h-5 text-blue-500" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{stats.users_with_telegram}</p>
                    <p className="text-xs text-muted-foreground">With Telegram</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-[#121212] border-white/5">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
                    <BarChart3 className="w-5 h-5 text-purple-500" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{stats.total_scans}</p>
                    <p className="text-xs text-muted-foreground">Total Scans</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Platform Stats */}
        {stats && (
          <div className="grid md:grid-cols-3 gap-4 mb-8">
            <Card className="bg-[#121212] border-white/5">
              <CardContent className="p-6 text-center">
                <Package className="w-8 h-8 text-primary mx-auto mb-2" />
                <p className="text-3xl font-bold">{stats.total_products}</p>
                <p className="text-sm text-muted-foreground">Products in Database</p>
              </CardContent>
            </Card>
            <Card className="bg-[#121212] border-white/5">
              <CardContent className="p-6 text-center">
                <Rocket className="w-8 h-8 text-blue-500 mx-auto mb-2" />
                <p className="text-3xl font-bold">{stats.total_launch_kits}</p>
                <p className="text-sm text-muted-foreground">Launch Kits Generated</p>
              </CardContent>
            </Card>
            <Card className="bg-[#121212] border-white/5">
              <CardContent className="p-6 text-center">
                <Search className="w-8 h-8 text-yellow-500 mx-auto mb-2" />
                <p className="text-3xl font-bold">{stats.total_competitors}</p>
                <p className="text-sm text-muted-foreground">Competitors Tracked</p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Users Table */}
        <Card className="bg-[#121212] border-white/5 mb-8">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Users ({totalUsers})</CardTitle>
              <div className="flex items-center gap-3">
                <div className="relative w-64">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input
                    placeholder="Search users..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 bg-[#0A0A0A] border-white/10"
                  />
                </div>
                <Button onClick={() => setShowAddUser(true)} className="bg-primary text-black font-bold">
                  <Plus className="w-4 h-4 mr-2" />
                  Add User
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/5">
                    <th className="text-left py-3 px-4 text-xs text-muted-foreground font-mono">USER</th>
                    <th className="text-left py-3 px-4 text-xs text-muted-foreground font-mono">EMAIL</th>
                    <th className="text-left py-3 px-4 text-xs text-muted-foreground font-mono">TIER</th>
                    <th className="text-left py-3 px-4 text-xs text-muted-foreground font-mono">INTEGRATIONS</th>
                    <th className="text-left py-3 px-4 text-xs text-muted-foreground font-mono">ACTIONS</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredUsers.map((u) => (
                    <tr key={u.id} className="border-b border-white/5 hover:bg-white/5">
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{u.name}</span>
                          {u.is_admin && <Badge className="bg-primary/20 text-primary text-xs">Admin</Badge>}
                        </div>
                      </td>
                      <td className="py-3 px-4 text-sm text-muted-foreground">{u.email}</td>
                      <td className="py-3 px-4">
                        <select
                          value={u.subscription_tier || 'free'}
                          onChange={(e) => handleUpdateTier(u.id, e.target.value)}
                          disabled={updatingTier === u.id}
                          className="bg-[#0A0A0A] border border-white/10 rounded px-2 py-1 text-sm capitalize"
                        >
                          {tiers.map(tier => (
                            <option key={tier} value={tier}>{tier}</option>
                          ))}
                        </select>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex gap-1">
                          {u.has_openai_key && (
                            <Badge variant="outline" className="text-xs text-green-500 border-green-500/30">OpenAI</Badge>
                          )}
                          {u.has_telegram && (
                            <Badge variant="outline" className="text-xs text-blue-500 border-blue-500/30">Telegram</Badge>
                          )}
                          {!u.has_openai_key && !u.has_telegram && (
                            <span className="text-xs text-muted-foreground">None</span>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex gap-1">
                          <Button 
                            variant="ghost" 
                            size="icon"
                            className="text-red-500 hover:text-red-400 hover:bg-red-500/10"
                            onClick={() => setShowDeleteConfirm(u)}
                            disabled={u.is_admin}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        {recentActivity && (
          <div className="grid md:grid-cols-2 gap-6">
            <Card className="bg-[#121212] border-white/5">
              <CardHeader>
                <CardTitle className="text-lg">Recent Scans</CardTitle>
              </CardHeader>
              <CardContent>
                {recentActivity.recent_scans.length === 0 ? (
                  <p className="text-sm text-muted-foreground text-center py-4">No recent scans</p>
                ) : (
                  <div className="space-y-3">
                    {recentActivity.recent_scans.slice(0, 5).map((scan, i) => (
                      <div key={i} className="flex items-center justify-between p-2 bg-white/5 rounded">
                        <div>
                          <p className="text-sm font-medium capitalize">{scan.scan_type?.replace('_', ' ')}</p>
                          <p className="text-xs text-muted-foreground">User: {scan.user_id?.slice(0, 8)}...</p>
                        </div>
                        <span className="text-xs text-muted-foreground">
                          {new Date(scan.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="bg-[#121212] border-white/5">
              <CardHeader>
                <CardTitle className="text-lg">Recent Launch Kits</CardTitle>
              </CardHeader>
              <CardContent>
                {recentActivity.recent_launch_kits.length === 0 ? (
                  <p className="text-sm text-muted-foreground text-center py-4">No recent launch kits</p>
                ) : (
                  <div className="space-y-3">
                    {recentActivity.recent_launch_kits.slice(0, 5).map((kit, i) => (
                      <div key={i} className="flex items-center justify-between p-2 bg-white/5 rounded">
                        <div>
                          <p className="text-sm font-medium">{kit.product_name}</p>
                          <p className="text-xs text-muted-foreground">User: {kit.user_id?.slice(0, 8)}...</p>
                        </div>
                        <Badge variant="outline" className="text-xs capitalize">{kit.status}</Badge>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </main>

      {/* Add User Modal */}
      <Dialog open={showAddUser} onOpenChange={setShowAddUser}>
        <DialogContent className="bg-[#121212] border-white/10">
          <DialogHeader>
            <DialogTitle>Add New User</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Name</Label>
              <Input
                value={newUser.name}
                onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
                className="bg-[#0A0A0A] border-white/10"
                placeholder="John Doe"
              />
            </div>
            <div className="space-y-2">
              <Label>Email</Label>
              <Input
                type="email"
                value={newUser.email}
                onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                className="bg-[#0A0A0A] border-white/10"
                placeholder="john@example.com"
              />
            </div>
            <div className="space-y-2">
              <Label>Password</Label>
              <Input
                type="password"
                value={newUser.password}
                onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                className="bg-[#0A0A0A] border-white/10"
                placeholder="••••••••"
              />
            </div>
            <div className="space-y-2">
              <Label>Subscription Tier</Label>
              <select
                value={newUser.subscription_tier}
                onChange={(e) => setNewUser({ ...newUser, subscription_tier: e.target.value })}
                className="w-full bg-[#0A0A0A] border border-white/10 rounded px-3 py-2 capitalize"
              >
                {tiers.map(tier => (
                  <option key={tier} value={tier}>{tier}</option>
                ))}
              </select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAddUser(false)}>Cancel</Button>
            <Button onClick={handleAddUser} disabled={addingUser} className="bg-primary text-black">
              {addingUser ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Create User'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Modal */}
      <Dialog open={!!showDeleteConfirm} onOpenChange={() => setShowDeleteConfirm(null)}>
        <DialogContent className="bg-[#121212] border-white/10">
          <DialogHeader>
            <DialogTitle className="text-red-500">Delete User</DialogTitle>
          </DialogHeader>
          <p className="text-muted-foreground py-4">
            Are you sure you want to delete <span className="text-white font-medium">{showDeleteConfirm?.name}</span> ({showDeleteConfirm?.email})? 
            This will also delete all their data including scan history, launch kits, and settings.
          </p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteConfirm(null)}>Cancel</Button>
            <Button 
              onClick={() => handleDeleteUser(showDeleteConfirm?.id)} 
              disabled={deletingUser}
              className="bg-red-500 hover:bg-red-600"
            >
              {deletingUser ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Delete User'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
