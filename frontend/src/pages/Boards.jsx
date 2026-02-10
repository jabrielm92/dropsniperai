import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import {
  ArrowLeft, BarChart3, Loader2, Plus, Package, Clock, ChevronRight
} from 'lucide-react';
import { toast } from 'sonner';
import { getBoards, createBoard } from '../lib/api';

export default function Boards() {
  const navigate = useNavigate();
  const [boards, setBoards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [newBoardName, setNewBoardName] = useState('');
  const [showCreate, setShowCreate] = useState(false);

  useEffect(() => {
    fetchBoards();
  }, []);

  const fetchBoards = async () => {
    try {
      const res = await getBoards();
      setBoards(res.data.boards || res.data || []);
    } catch (error) {
      console.error('Failed to load boards:', error);
      toast.error('Failed to load boards');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateBoard = async () => {
    if (!newBoardName.trim()) {
      toast.error('Board name is required');
      return;
    }
    setCreating(true);
    try {
      await createBoard(newBoardName.trim());
      toast.success('Board created!');
      setNewBoardName('');
      setShowCreate(false);
      fetchBoards();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create board');
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0A0A]">
      <header className="border-b border-white/5 bg-[#0A0A0A]/80 backdrop-blur sticky top-0 z-50">
        <div className="flex items-center justify-between px-6 py-4">
          <Button
            variant="ghost"
            onClick={() => navigate('/dashboard')}
            className="text-muted-foreground hover:text-white"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Dashboard
          </Button>
          <h1 className="text-lg font-bold">Product Boards</h1>
          <Button
            size="sm"
            onClick={() => setShowCreate(!showCreate)}
            className="bg-primary text-black font-semibold hover:bg-primary/90"
          >
            <Plus className="w-3.5 h-3.5 mr-1" />
            New Board
          </Button>
        </div>
      </header>

      <main className="p-6 max-w-[1200px] mx-auto">
        {/* Create Board Form */}
        {showCreate && (
          <Card className="bg-[#111] border-primary/20 mb-6">
            <CardContent className="p-4">
              <p className="text-sm font-medium mb-3">Create New Board</p>
              <div className="flex gap-3">
                <input
                  type="text"
                  placeholder="Board name..."
                  value={newBoardName}
                  onChange={(e) => setNewBoardName(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleCreateBoard()}
                  className="flex-1 px-3 py-2 bg-[#0A0A0A] border border-white/[0.08] rounded-lg text-sm focus:outline-none focus:border-primary/40 placeholder:text-white/30"
                  autoFocus
                />
                <Button
                  onClick={handleCreateBoard}
                  disabled={creating}
                  size="sm"
                  className="bg-primary text-black font-semibold"
                >
                  {creating ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Create'}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => { setShowCreate(false); setNewBoardName(''); }}
                >
                  Cancel
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-6 h-6 animate-spin text-primary" />
          </div>
        ) : boards.length === 0 ? (
          <Card className="bg-[#111] border-white/[0.06] border-dashed">
            <CardContent className="py-16 text-center">
              <BarChart3 className="w-10 h-10 mx-auto mb-3 text-white/20" />
              <p className="font-medium mb-1">No boards yet</p>
              <p className="text-sm text-muted-foreground mb-4">
                Create a board to organize and save your favorite products
              </p>
              <Button
                onClick={() => setShowCreate(true)}
                size="sm"
                className="bg-primary text-black font-semibold"
              >
                <Plus className="w-3.5 h-3.5 mr-1.5" />
                Create First Board
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {boards.map((board, index) => (
              <Card
                key={board.id || index}
                className="bg-[#111] border-white/[0.06] hover:border-amber-500/20 cursor-pointer transition-all group"
              >
                <CardContent className="p-5">
                  <div className="flex items-start justify-between mb-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500/20 to-amber-500/5 flex items-center justify-center">
                      <BarChart3 className="w-5 h-5 text-amber-400" />
                    </div>
                    <ChevronRight className="w-4 h-4 text-white/20 group-hover:text-amber-400 transition-colors" />
                  </div>

                  <h3 className="font-semibold mb-1">{board.name}</h3>
                  {board.description && (
                    <p className="text-xs text-muted-foreground mb-3 line-clamp-2">{board.description}</p>
                  )}

                  <div className="flex items-center gap-3 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Package className="w-3 h-3" />
                      {board.product_ids?.length || 0} products
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {board.created_at ? new Date(board.created_at).toLocaleDateString() : 'Unknown'}
                    </span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
