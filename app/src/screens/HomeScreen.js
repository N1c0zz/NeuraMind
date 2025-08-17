import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  Alert,
  Dimensions,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  FAB,
  Surface,
  Text,
  IconButton,
} from 'react-native-paper';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS, SIZES, CONFIG } from '../utils/constants';
import apiService from '../services/apiService';

const { width } = Dimensions.get('window');

export default function HomeScreen({ navigation }) {
  const [isOnline, setIsOnline] = useState(false);
  const [stats, setStats] = useState({
    documents: 0,
    lastUpload: null,
  });

  useEffect(() => {
    checkHealth();
    loadStats();
  }, []);

  const checkHealth = async () => {
    try {
      await apiService.healthCheck();
      setIsOnline(true);
    } catch (error) {
      setIsOnline(false);
      console.error('Backend not reachable:', error);
    }
  };

  const loadStats = async () => {
    try {
      // Per ora stats semplici, in futuro potresti implementare un endpoint dedicato
      setStats({
        documents: 0, // Verrà aggiornato quando implementeremo la lista documenti
        lastUpload: null,
      });
    } catch (error) {
      console.error('Error loading stats:', error);
      setStats({
        documents: 0,
        lastUpload: null,
      });
    }
  };

  const showConnectionAlert = () => {
    Alert.alert(
      'Stato Connessione',
      isOnline 
        ? 'Connesso al backend NeuraMind ✅' 
        : 'Backend non raggiungibile ❌\n\nVerifica che il server Railway sia attivo.',
      [{ text: 'OK' }]
    );
  };

  return (
    <View style={styles.container}>
      <ScrollView 
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header con gradiente */}
        <LinearGradient
          colors={[COLORS.primary, COLORS.secondary, COLORS.accent]}
          style={styles.headerGradient}
        >
          <View style={styles.headerContent}>
            <View style={styles.headerTop}>
              <Title style={styles.headerTitle}>NeuraMind</Title>
              <IconButton
                icon={isOnline ? 'wifi' : 'wifi-off'}
                iconColor={isOnline ? COLORS.success : COLORS.error}
                size={24}
                onPress={showConnectionAlert}
              />
            </View>
            <Paragraph style={styles.headerSubtitle}>
              Il tuo assistente AI personale per documenti
            </Paragraph>
          </View>
        </LinearGradient>

        {/* Cards principali */}
        <View style={styles.cardsContainer}>
          {/* Card Chat */}
          <Card style={styles.mainCard} elevation={4}>
            <Card.Content>
              <View style={styles.cardHeader}>
                <IconButton
                  icon="chat"
                  iconColor={COLORS.blue}
                  size={40}
                />
                <View style={styles.cardText}>
                  <Title style={styles.cardTitle}>Chatta con i tuoi documenti</Title>
                  <Paragraph style={styles.cardSubtitle}>
                    Fai domande sui documenti caricati
                  </Paragraph>
                </View>
              </View>
            </Card.Content>
            <Card.Actions>
              <Button
                mode="contained"
                onPress={() => navigation.navigate('Chat')}
                style={styles.primaryButton}
                disabled={!isOnline}
              >
                Apri Chat
              </Button>
            </Card.Actions>
          </Card>

          {/* Card Upload */}
          <Card style={styles.mainCard} elevation={4}>
            <Card.Content>
              <View style={styles.cardHeader}>
                <IconButton
                  icon="upload"
                  iconColor={COLORS.purple}
                  size={40}
                />
                <View style={styles.cardText}>
                  <Title style={styles.cardTitle}>Carica documenti</Title>
                  <Paragraph style={styles.cardSubtitle}>
                    Scatta foto o seleziona file
                  </Paragraph>
                </View>
              </View>
            </Card.Content>
            <Card.Actions>
              <Button
                mode="contained"
                onPress={() => navigation.navigate('Upload')}
                style={styles.secondaryButton}
                disabled={!isOnline}
              >
                Carica
              </Button>
            </Card.Actions>
          </Card>

          {/* Card Documenti */}
          <Card style={styles.mainCard} elevation={4}>
            <Card.Content>
              <View style={styles.cardHeader}>
                <IconButton
                  icon="folder"
                  iconColor={COLORS.accent}
                  size={40}
                />
                <View style={styles.cardText}>
                  <Title style={styles.cardTitle}>I miei documenti</Title>
                  <Paragraph style={styles.cardSubtitle}>
                    {stats.documents} documenti caricati
                  </Paragraph>
                </View>
              </View>
            </Card.Content>
            <Card.Actions>
              <Button
                mode="outlined"
                onPress={() => navigation.navigate('Documents')}
                disabled={!isOnline}
              >
                Visualizza
              </Button>
            </Card.Actions>
          </Card>
        </View>

        {/* Statistiche */}
        <Surface style={styles.statsCard} elevation={2}>
          <Title style={styles.statsTitle}>Statistiche</Title>
          <View style={styles.statsRow}>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>{stats.documents}</Text>
              <Text style={styles.statLabel}>Documenti</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>
                {isOnline ? '✅' : '❌'}
              </Text>
              <Text style={styles.statLabel}>Stato</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>0</Text>
              <Text style={styles.statLabel}>Chat</Text>
            </View>
          </View>
        </Surface>

        {/* Informazioni app */}
        <Surface style={styles.infoCard} elevation={1}>
          <Title style={styles.infoTitle}>Come funziona?</Title>
          <View style={styles.infoSteps}>
            <View style={styles.infoStep}>
              <Text style={styles.stepNumber}>1</Text>
              <Text style={styles.stepText}>Carica documenti (foto o file)</Text>
            </View>
            <View style={styles.infoStep}>
              <Text style={styles.stepNumber}>2</Text>
              <Text style={styles.stepText}>L'AI analizza e indicizza il contenuto</Text>
            </View>
            <View style={styles.infoStep}>
              <Text style={styles.stepNumber}>3</Text>
              <Text style={styles.stepText}>Fai domande sui tuoi documenti</Text>
            </View>
          </View>
        </Surface>
      </ScrollView>

      {/* FAB per chat rapida */}
      <FAB
        icon="message"
        style={styles.fab}
        onPress={() => navigation.navigate('Chat')}
        disabled={!isOnline}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 100,
  },
  headerGradient: {
    paddingTop: SIZES.padding * 2,
    paddingBottom: SIZES.padding * 3,
    paddingHorizontal: SIZES.padding,
  },
  headerContent: {
    alignItems: 'center',
  },
  headerTop: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    width: '100%',
  },
  headerTitle: {
    color: 'white',
    fontSize: 28,
    fontWeight: 'bold',
  },
  headerSubtitle: {
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: 16,
    textAlign: 'center',
    marginTop: SIZES.margin,
  },
  cardsContainer: {
    padding: SIZES.padding,
    marginTop: -SIZES.padding * 2,
  },
  mainCard: {
    marginBottom: SIZES.padding,
    borderRadius: SIZES.borderRadius,
    backgroundColor: COLORS.surface,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  cardText: {
    flex: 1,
    marginLeft: SIZES.margin,
  },
  cardTitle: {
    fontSize: 18,
    color: COLORS.text,
  },
  cardSubtitle: {
    color: COLORS.textLight,
    fontSize: 14,
  },
  primaryButton: {
    backgroundColor: COLORS.blue,
  },
  secondaryButton: {
    backgroundColor: COLORS.purple,
  },
  statsCard: {
    margin: SIZES.padding,
    marginTop: 0,
    padding: SIZES.padding,
    borderRadius: SIZES.borderRadius,
    backgroundColor: COLORS.surface,
  },
  statsTitle: {
    textAlign: 'center',
    marginBottom: SIZES.padding,
    color: COLORS.text,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.primary,
  },
  statLabel: {
    fontSize: 12,
    color: COLORS.textLight,
    marginTop: 4,
  },
  infoCard: {
    margin: SIZES.padding,
    marginTop: 0,
    padding: SIZES.padding,
    borderRadius: SIZES.borderRadius,
    backgroundColor: COLORS.surface,
  },
  infoTitle: {
    textAlign: 'center',
    marginBottom: SIZES.padding,
    color: COLORS.text,
  },
  infoSteps: {
    gap: SIZES.margin,
  },
  infoStep: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  stepNumber: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: COLORS.accent,
    color: 'white',
    textAlign: 'center',
    lineHeight: 30,
    fontWeight: 'bold',
    marginRight: SIZES.margin,
  },
  stepText: {
    flex: 1,
    color: COLORS.text,
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
    backgroundColor: COLORS.blue,
  },
});
