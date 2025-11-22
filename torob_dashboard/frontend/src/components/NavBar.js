import React from 'react';
import { AppBar, Toolbar, Typography, Box } from '@mui/material';
import { Store as StoreIcon } from '@mui/icons-material';

const NavBar = () => {
  return (
    <AppBar position="static">
      <Toolbar>
        <StoreIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          داشبورد جغرافیایی بازار ترب
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Typography variant="body2">
            تحلیل داده‌های بازار
          </Typography>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default NavBar;
