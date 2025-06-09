import React from 'react';
import { Box, AppBar, Toolbar, Typography, IconButton, Drawer, List, ListItem, ListItemIcon, ListItemText, useTheme } from '@mui/material';
import { Menu as MenuIcon, Dashboard as DashboardIcon, ExitToApp as LogoutIcon } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [drawerOpen, setDrawerOpen] = React.useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const theme = useTheme();

  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, onClick: () => navigate('/') },
    { text: 'Logout', icon: <LogoutIcon />, onClick: handleLogout },
  ];

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppBar position="fixed" sx={{ zIndex: theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div">
            PO Generator
          </Typography>
          {user && (
            <Typography variant="subtitle1" sx={{ ml: 'auto', mr: 2 }}>
              {user.name}
            </Typography>
          )}
        </Toolbar>
      </AppBar>

      <Drawer
        variant="temporary"
        anchor="left"
        open={drawerOpen}
        onClose={handleDrawerToggle}
        sx={{
          width: 240,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: 240,
            boxSizing: 'border-box',
          },
        }}
      >
        <Toolbar /> {/* This creates space for the AppBar */}
        <List>
          {menuItems.map((item) => (
            <ListItem 
              key={item.text} 
              onClick={item.onClick}
              sx={{ cursor: 'pointer' }}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItem>
          ))}
        </List>
      </Drawer>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: '100%',
          mt: '64px', // Height of AppBar
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

export default Layout; 