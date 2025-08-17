import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { Provider as PaperProvider } from 'react-native-paper';
import { StatusBar } from 'expo-status-bar';
import { COLORS } from './src/utils/constants';

// Screens
import HomeScreen from './src/screens/HomeScreen';
import ChatScreen from './src/screens/ChatScreen';
import DocumentsScreen from './src/screens/DocumentsScreen';
import UploadScreen from './src/screens/UploadScreen';

const Stack = createStackNavigator();

const theme = {
  colors: {
    primary: COLORS.primary,
    background: COLORS.background,
    surface: COLORS.surface,
    accent: COLORS.accent,
    error: COLORS.error,
    text: COLORS.text,
    onSurface: COLORS.text,
    disabled: COLORS.textLight,
    placeholder: COLORS.textLight,
    backdrop: 'rgba(0, 0, 0, 0.5)',
    notification: COLORS.accent,
  },
};

export default function App() {
  return (
    <PaperProvider theme={theme}>
      <NavigationContainer>
        <StatusBar style="light" backgroundColor={COLORS.primary} />
        <Stack.Navigator
          initialRouteName="Home"
          screenOptions={{
            headerStyle: {
              backgroundColor: COLORS.primary,
            },
            headerTintColor: '#fff',
            headerTitleStyle: {
              fontWeight: 'bold',
            },
          }}
        >
          <Stack.Screen 
            name="Home" 
            component={HomeScreen}
            options={{
              title: 'NeuraMind',
              headerStyle: {
                backgroundColor: COLORS.primary,
              },
            }}
          />
          <Stack.Screen 
            name="Chat" 
            component={ChatScreen}
            options={{
              title: 'Assistente AI',
            }}
          />
          <Stack.Screen 
            name="Documents" 
            component={DocumentsScreen}
            options={{
              title: 'I Miei Documenti',
            }}
          />
          <Stack.Screen 
            name="Upload" 
            component={UploadScreen}
            options={{
              title: 'Carica Documento',
            }}
          />
        </Stack.Navigator>
      </NavigationContainer>
    </PaperProvider>
  );
}
