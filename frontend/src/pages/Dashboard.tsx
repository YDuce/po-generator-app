import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Container,
  Typography,
  CircularProgress,
  Alert,
  Snackbar,
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

export default function Dashboard() {
  const { user, logout, loading, error } = useAuth();
  const navigate = useNavigate();
  const [logoutLoading, setLogoutLoading] = useState(false);
  const [showError, setShowError] = useState(false);

  const handleLogout = async () => {
    try {
      setLogoutLoading(true);
      await logout();
      navigate('/login', { replace: true });
    } catch (err) {
      setShowError(true);
    } finally {
      setLogoutLoading(false);
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mb: 4,
          }}
        >
          <Typography variant="h4">Dashboard</Typography>
          <Button
            variant="outlined"
            color="primary"
            onClick={handleLogout}
            disabled={logoutLoading}
            startIcon={logoutLoading ? <CircularProgress size={20} /> : null}
          >
            {logoutLoading ? 'Logging out...' : 'Logout'}
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Typography variant="body1">
            Welcome, {user?.name}! You are successfully authenticated.
          </Typography>
        )}

        <Snackbar
          open={showError}
          autoHideDuration={6000}
          onClose={() => setShowError(false)}
          message="Failed to logout. Please try again."
        />
      </Box>
    </Container>
  );
} 