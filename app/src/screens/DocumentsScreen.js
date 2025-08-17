import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  FlatList,
  RefreshControl,
  Alert,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  Text,
  Surface,
  ActivityIndicator,
  Searchbar,
  Chip,
  IconButton,
} from 'react-native-paper';
import { COLORS, SIZES, CONFIG, MESSAGES } from '../utils/constants';
import apiService from '../services/apiService';

export default function DocumentsScreen({ navigation }) {
  const [documents, setDocuments] = useState([]);
  const [filteredDocuments, setFilteredDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadDocuments();
  }, []);

  useEffect(() => {
    filterDocuments();
  }, [documents, searchQuery]);

  const loadDocuments = async () => {
    try {
      setIsLoading(true);
      
      // Carica documenti reali dal backend
      const response = await apiService.listDocuments(CONFIG.USER_ID);
      
      // Converti i documenti dal backend al formato dell'app
      const formattedDocuments = response.documents.map(doc => ({
        id: doc.item_id,
        title: doc.title,
        uploadDate: new Date(doc.upload_date || doc.created_at),
        type: doc.file_type === 'application/pdf' ? 'PDF' : 'Immagine',
        size: `${Math.round(doc.text_length / 1024)} KB`, // Approssimazione
        chunks: doc.chunks_count,
        language: 'ita+eng', // Default, potresti salvarlo nei metadata
        thumbnail: null,
        textPreview: doc.text_preview,
        ocrConfidence: doc.ocr_confidence,
      }));
      
      setDocuments(formattedDocuments);
      
    } catch (error) {
      console.error('Error loading documents:', error);
      Alert.alert(
        'Errore',
        MESSAGES.documents.error,
        [{ text: 'OK' }]
      );
      setDocuments([]); // Fallback sicuro
    } finally {
      setIsLoading(false);
    }
  };

  const refreshDocuments = async () => {
    setIsRefreshing(true);
    await loadDocuments();
    setIsRefreshing(false);
  };

  const filterDocuments = () => {
    if (!searchQuery.trim()) {
      setFilteredDocuments(documents);
      return;
    }

    const filtered = documents.filter(doc =>
      doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.type.toLowerCase().includes(searchQuery.toLowerCase())
    );
    
    setFilteredDocuments(filtered);
  };

  const deleteDocument = async (documentId) => {
    Alert.alert(
      'Elimina documento',
      'Sei sicuro di voler eliminare questo documento? Questa azione non può essere annullata.',
      [
        { text: 'Annulla', style: 'cancel' },
        {
          text: 'Elimina',
          style: 'destructive',
          onPress: async () => {
            try {
              setIsLoading(true);
              
              // Elimina dal backend
              await apiService.deleteDocument(CONFIG.USER_ID, documentId);
              
              // Aggiorna la lista locale
              setDocuments(prev => prev.filter(doc => doc.id !== documentId));
              
              Alert.alert('Successo', 'Documento eliminato con successo');
            } catch (error) {
              console.error('Error deleting document:', error);
              Alert.alert('Errore', 'Impossibile eliminare il documento');
            } finally {
              setIsLoading(false);
            }
          }
        }
      ]
    );
  };

  const askAboutDocument = (document) => {
    navigation.navigate('Chat');
    // Potresti anche pre-riempire la chat con una domanda specifica sul documento
  };

  const formatDate = (date) => {
    return date.toLocaleDateString('it-IT', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  const getTypeColor = (type) => {
    switch (type.toLowerCase()) {
      case 'pdf':
        return COLORS.error;
      case 'immagine':
        return COLORS.blue;
      default:
        return COLORS.textLight;
    }
  };

  const getLanguageLabel = (language) => {
    const lang = CONFIG.OCR_LANGUAGES.find(l => l.value === language);
    return lang ? lang.label : language;
  };

  const renderDocument = ({ item }) => (
    <Card style={styles.documentCard} elevation={2}>
      <Card.Content>
        <View style={styles.documentHeader}>
          <View style={styles.documentInfo}>
            <Title style={styles.documentTitle} numberOfLines={2}>
              {item.title}
            </Title>
            <Text style={styles.documentDate}>
              Caricato il {formatDate(item.uploadDate)}
            </Text>
          </View>
          <IconButton
            icon="delete"
            iconColor={COLORS.error}
            size={20}
            onPress={() => deleteDocument(item.id)}
          />
        </View>

        <View style={styles.documentTags}>
          <Chip
            style={[styles.chip, { backgroundColor: getTypeColor(item.type) + '20' }]}
            textStyle={{ color: getTypeColor(item.type) }}
          >
            {item.type}
          </Chip>
          <Chip style={styles.chip} textStyle={styles.chipText}>
            {item.size}
          </Chip>
          <Chip style={styles.chip} textStyle={styles.chipText}>
            {item.chunks} chunks
          </Chip>
        </View>

        <Paragraph style={styles.documentDetails}>
          Lingua: {getLanguageLabel(item.language)}
          {item.ocrConfidence && (
            <Text style={styles.confidenceText}> • OCR: {(item.ocrConfidence * 100).toFixed(1)}%</Text>
          )}
        </Paragraph>
        
        {item.textPreview && (
          <Paragraph style={styles.textPreview} numberOfLines={2}>
            {item.textPreview}
          </Paragraph>
        )}
      </Card.Content>

      <Card.Actions>
        <Button
          mode="text"
          onPress={() => askAboutDocument(item)}
          icon="chat"
        >
          Chiedi info
        </Button>
        <Button
          mode="outlined"
          onPress={() => {
            // Implementa visualizzazione dettagli
            Alert.alert('Info', `Documento: ${item.title}\nCaricato: ${formatDate(item.uploadDate)}\nDimensione: ${item.size}\nChunks: ${item.chunks}`);
          }}
        >
          Dettagli
        </Button>
      </Card.Actions>
    </Card>
  );

  const renderEmptyState = () => (
    <View style={styles.emptyContainer}>
      <Surface style={styles.emptyCard} elevation={1}>
        <Title style={styles.emptyTitle}>Nessun documento</Title>
        <Paragraph style={styles.emptyText}>
          {MESSAGES.documents.empty}
        </Paragraph>
        <Button
          mode="contained"
          icon="upload"
          onPress={() => navigation.navigate('Upload')}
          style={styles.emptyButton}
        >
          Carica primo documento
        </Button>
      </Surface>
    </View>
  );

  const renderHeader = () => (
    <View style={styles.header}>
      <Searchbar
        placeholder="Cerca documenti..."
        onChangeText={setSearchQuery}
        value={searchQuery}
        style={styles.searchBar}
      />
      
      <View style={styles.statsContainer}>
        <Surface style={styles.statCard} elevation={1}>
          <Text style={styles.statNumber}>{documents.length}</Text>
          <Text style={styles.statLabel}>Documenti</Text>
        </Surface>
        <Surface style={styles.statCard} elevation={1}>
          <Text style={styles.statNumber}>
            {documents.reduce((sum, doc) => sum + doc.chunks, 0)}
          </Text>
          <Text style={styles.statLabel}>Chunks totali</Text>
        </Surface>
        <Surface style={styles.statCard} elevation={1}>
          <Text style={styles.statNumber}>10</Text>
          <Text style={styles.statLabel}>Limite max</Text>
        </Surface>
      </View>
      
      {documents.length >= 10 && (
        <Surface style={styles.warningCard} elevation={1}>
          <Text style={styles.warningText}>
            ⚠️ Limite raggiunto: I nuovi documenti sostituiranno automaticamente quelli più vecchi
          </Text>
        </Surface>
      )}
    </View>
  );

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={COLORS.primary} />
        <Text style={styles.loadingText}>Caricamento documenti...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={filteredDocuments}
        renderItem={renderDocument}
        keyExtractor={item => item.id}
        ListHeaderComponent={renderHeader}
        ListEmptyComponent={renderEmptyState}
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={isRefreshing}
            onRefresh={refreshDocuments}
            colors={[COLORS.primary]}
          />
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: COLORS.background,
  },
  loadingText: {
    marginTop: SIZES.margin,
    color: COLORS.text,
  },
  listContent: {
    padding: SIZES.padding,
    paddingBottom: SIZES.padding * 2,
  },
  header: {
    marginBottom: SIZES.padding,
  },
  searchBar: {
    marginBottom: SIZES.padding,
    backgroundColor: COLORS.surface,
  },
  statsContainer: {
    flexDirection: 'row',
    gap: SIZES.margin,
    marginBottom: SIZES.padding,
  },
  statCard: {
    flex: 1,
    padding: SIZES.padding,
    borderRadius: SIZES.borderRadius,
    alignItems: 'center',
    backgroundColor: COLORS.surface,
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
  documentCard: {
    marginBottom: SIZES.padding,
    borderRadius: SIZES.borderRadius,
    backgroundColor: COLORS.surface,
  },
  documentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: SIZES.margin,
  },
  documentInfo: {
    flex: 1,
  },
  documentTitle: {
    fontSize: 18,
    color: COLORS.text,
    marginBottom: 4,
  },
  documentDate: {
    fontSize: 12,
    color: COLORS.textLight,
  },
  documentTags: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: SIZES.margin / 2,
    marginBottom: SIZES.margin,
  },
  chip: {
    height: 28,
  },
  chipText: {
    fontSize: 12,
    color: COLORS.textLight,
  },
  documentDetails: {
    fontSize: 14,
    color: COLORS.textLight,
    marginBottom: 0,
  },
  confidenceText: {
    fontWeight: 'bold',
    color: COLORS.success,
  },
  textPreview: {
    fontSize: 12,
    color: COLORS.textLight,
    fontStyle: 'italic',
    marginTop: SIZES.margin / 2,
    lineHeight: 16,
  },
  warningCard: {
    padding: SIZES.padding,
    borderRadius: SIZES.borderRadius,
    backgroundColor: COLORS.warning + '20',
    marginBottom: SIZES.padding,
  },
  warningText: {
    color: COLORS.warning,
    fontSize: 14,
    textAlign: 'center',
    fontWeight: '500',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: SIZES.padding * 3,
  },
  emptyCard: {
    padding: SIZES.padding * 2,
    borderRadius: SIZES.borderRadius,
    alignItems: 'center',
    backgroundColor: COLORS.surface,
    width: '100%',
    maxWidth: 300,
  },
  emptyTitle: {
    fontSize: 20,
    color: COLORS.text,
    marginBottom: SIZES.margin,
    textAlign: 'center',
  },
  emptyText: {
    fontSize: 16,
    color: COLORS.textLight,
    textAlign: 'center',
    marginBottom: SIZES.padding,
  },
  emptyButton: {
    backgroundColor: COLORS.blue,
  },
});
