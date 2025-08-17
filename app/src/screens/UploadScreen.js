import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  Alert,
  Image,
  Platform,
} from 'react-native';
import {
  Card,
  Title,
  Button,
  TextInput,
  Text,
  Surface,
  ActivityIndicator,
  List,
  RadioButton,
} from 'react-native-paper';
import * as ImagePicker from 'expo-image-picker';
import * as DocumentPicker from 'expo-document-picker';
import { COLORS, SIZES, CONFIG, MESSAGES } from '../utils/constants';
import apiService from '../services/apiService';

export default function UploadScreen({ navigation }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [title, setTitle] = useState('');
  const [language, setLanguage] = useState('ita+eng');
  const [isUploading, setIsUploading] = useState(false);
  const [showLanguageSelector, setShowLanguageSelector] = useState(false);

  const requestCameraPermission = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert(
        'Permesso richiesto',
        MESSAGES.camera.permission,
        [{ text: 'OK' }]
      );
      return false;
    }
    return true;
  };

  const takePhoto = async () => {
    const hasPermission = await requestCameraPermission();
    if (!hasPermission) return;

    try {
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled) {
        setSelectedFile({
          uri: result.assets[0].uri,
          type: 'image',
          name: `photo_${Date.now()}.jpg`,
          mimeType: 'image/jpeg',
        });
      }
    } catch (error) {
      console.error('Error taking photo:', error);
      Alert.alert('Errore', MESSAGES.camera.error);
    }
  };

  const pickImage = async () => {
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled) {
        setSelectedFile({
          uri: result.assets[0].uri,
          type: 'image',
          name: `image_${Date.now()}.jpg`,
          mimeType: 'image/jpeg',
        });
      }
    } catch (error) {
      console.error('Error picking image:', error);
      Alert.alert('Errore', 'Errore durante la selezione dell\'immagine');
    }
  };

  const pickDocument = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ['image/*', 'application/pdf'],
        copyToCacheDirectory: true,
      });

      if (!result.canceled) {
        const file = result.assets[0];
        
        // Verifica dimensione file
        if (file.size && file.size > CONFIG.MAX_FILE_SIZE) {
          Alert.alert(
            'File troppo grande',
            'Il file selezionato supera i 10MB. Seleziona un file più piccolo.',
            [{ text: 'OK' }]
          );
          return;
        }

        setSelectedFile({
          uri: file.uri,
          type: file.mimeType?.startsWith('image/') ? 'image' : 'document',
          name: file.name,
          mimeType: file.mimeType,
        });
      }
    } catch (error) {
      console.error('Error picking document:', error);
      Alert.alert('Errore', 'Errore durante la selezione del documento');
    }
  };

  const uploadDocument = async () => {
    if (!selectedFile) {
      Alert.alert('Errore', 'Seleziona un file prima di procedere');
      return;
    }

    if (!title.trim()) {
      Alert.alert('Errore', 'Inserisci un titolo per il documento');
      return;
    }

    setIsUploading(true);

    try {
      const response = await apiService.uploadDocument(
        selectedFile.uri,
        title.trim(),
        CONFIG.USER_ID,
        language
      );

      Alert.alert(
        'Successo',
        MESSAGES.upload.success,
        [
          {
            text: 'OK',
            onPress: () => {
              // Reset form
              setSelectedFile(null);
              setTitle('');
              setLanguage('ita+eng');
              // Torna alla home
              navigation.goBack();
            }
          }
        ]
      );

    } catch (error) {
      console.error('Upload error:', error);
      Alert.alert(
        'Errore',
        MESSAGES.upload.error + '\n\n' + (error.message || 'Errore sconosciuto'),
        [{ text: 'OK' }]
      );
    } finally {
      setIsUploading(false);
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
  };

  const getLanguageLabel = (langCode) => {
    const lang = CONFIG.OCR_LANGUAGES.find(l => l.value === langCode);
    return lang ? lang.label : langCode;
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Selezione file */}
      <Card style={styles.card} elevation={3}>
        <Card.Content>
          <Title style={styles.cardTitle}>Seleziona documento</Title>
          
          {!selectedFile ? (
            <View style={styles.buttonContainer}>
              <Button
                mode="contained"
                icon="camera"
                onPress={takePhoto}
                style={[styles.button, styles.primaryButton]}
                contentStyle={styles.buttonContent}
              >
                Scatta foto
              </Button>
              
              <Button
                mode="contained"
                icon="image"
                onPress={pickImage}
                style={[styles.button, styles.secondaryButton]}
                contentStyle={styles.buttonContent}
              >
                Dalla galleria
              </Button>
              
              <Button
                mode="outlined"
                icon="file"
                onPress={pickDocument}
                style={styles.button}
                contentStyle={styles.buttonContent}
              >
                Scegli file
              </Button>
            </View>
          ) : (
            <View style={styles.selectedFileContainer}>
              {selectedFile.type === 'image' && (
                <Image source={{ uri: selectedFile.uri }} style={styles.previewImage} />
              )}
              
              <Surface style={styles.fileInfo} elevation={1}>
                <Text style={styles.fileName}>{selectedFile.name}</Text>
                <Text style={styles.fileType}>
                  {selectedFile.type === 'image' ? 'Immagine' : 'Documento'}
                </Text>
              </Surface>
              
              <Button
                mode="text"
                icon="close"
                onPress={removeFile}
                style={styles.removeButton}
              >
                Rimuovi
              </Button>
            </View>
          )}
        </Card.Content>
      </Card>

      {/* Dettagli documento */}
      {selectedFile && (
        <Card style={styles.card} elevation={3}>
          <Card.Content>
            <Title style={styles.cardTitle}>Dettagli documento</Title>
            
            <TextInput
              label="Titolo documento *"
              value={title}
              onChangeText={setTitle}
              mode="outlined"
              style={styles.textInput}
              placeholder="es. Contratto, Fattura, Appunti..."
              maxLength={100}
            />
            
            <View style={styles.languageContainer}>
              <Text style={styles.languageLabel}>Lingua per OCR:</Text>
              <Button
                mode="outlined"
                onPress={() => setShowLanguageSelector(!showLanguageSelector)}
                style={styles.languageButton}
              >
                {getLanguageLabel(language)}
              </Button>
            </View>
            
            {showLanguageSelector && (
              <Surface style={styles.languageSelector} elevation={1}>
                <RadioButton.Group
                  onValueChange={value => {
                    setLanguage(value);
                    setShowLanguageSelector(false);
                  }}
                  value={language}
                >
                  {CONFIG.OCR_LANGUAGES.map(lang => (
                    <RadioButton.Item
                      key={lang.value}
                      label={lang.label}
                      value={lang.value}
                      style={styles.radioItem}
                    />
                  ))}
                </RadioButton.Group>
              </Surface>
            )}
          </Card.Content>
        </Card>
      )}

      {/* Pulsante upload */}
      {selectedFile && title.trim() && (
        <Card style={styles.card} elevation={3}>
          <Card.Content>
            <Title style={styles.cardTitle}>Carica documento</Title>
            <Text style={styles.uploadDescription}>
              Il documento verrà analizzato con OCR e indicizzato per le ricerche.
            </Text>
            
            {isUploading ? (
              <View style={styles.uploadingContainer}>
                <ActivityIndicator size="large" color={COLORS.primary} />
                <Text style={styles.uploadingText}>{MESSAGES.upload.processing}</Text>
              </View>
            ) : (
              <Button
                mode="contained"
                icon="upload"
                onPress={uploadDocument}
                style={[styles.button, styles.uploadButton]}
                contentStyle={styles.buttonContent}
              >
                Carica e analizza
              </Button>
            )}
          </Card.Content>
        </Card>
      )}

      {/* Informazioni */}
      <Surface style={styles.infoCard} elevation={1}>
        <Title style={styles.infoTitle}>Formati supportati</Title>
        <View style={styles.infoList}>
          <Text style={styles.infoItem}>• Immagini: JPEG, PNG</Text>
          <Text style={styles.infoItem}>• Documenti: PDF (come immagine)</Text>
          <Text style={styles.infoItem}>• Dimensione massima: 10MB</Text>
          <Text style={styles.infoItem}>• L'OCR riconosce il testo nelle immagini</Text>
        </View>
      </Surface>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  content: {
    padding: SIZES.padding,
    paddingBottom: SIZES.padding * 2,
  },
  card: {
    marginBottom: SIZES.padding,
    borderRadius: SIZES.borderRadius,
  },
  cardTitle: {
    color: COLORS.text,
    marginBottom: SIZES.padding,
  },
  buttonContainer: {
    gap: SIZES.margin,
  },
  button: {
    marginVertical: SIZES.margin / 2,
  },
  buttonContent: {
    paddingVertical: SIZES.margin / 2,
  },
  primaryButton: {
    backgroundColor: COLORS.blue,
  },
  secondaryButton: {
    backgroundColor: COLORS.purple,
  },
  selectedFileContainer: {
    alignItems: 'center',
  },
  previewImage: {
    width: 200,
    height: 150,
    borderRadius: SIZES.borderRadius,
    marginBottom: SIZES.margin,
  },
  fileInfo: {
    padding: SIZES.padding,
    borderRadius: SIZES.borderRadius,
    alignItems: 'center',
    marginBottom: SIZES.margin,
  },
  fileName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: COLORS.text,
    textAlign: 'center',
  },
  fileType: {
    fontSize: 14,
    color: COLORS.textLight,
    marginTop: 4,
  },
  removeButton: {
    marginTop: SIZES.margin,
  },
  textInput: {
    marginBottom: SIZES.padding,
    backgroundColor: COLORS.background,
  },
  languageContainer: {
    marginBottom: SIZES.padding,
  },
  languageLabel: {
    fontSize: 16,
    color: COLORS.text,
    marginBottom: SIZES.margin,
  },
  languageButton: {
    alignSelf: 'flex-start',
  },
  languageSelector: {
    marginTop: SIZES.margin,
    borderRadius: SIZES.borderRadius,
    backgroundColor: COLORS.surface,
  },
  radioItem: {
    paddingVertical: 4,
  },
  uploadDescription: {
    color: COLORS.textLight,
    marginBottom: SIZES.padding,
    textAlign: 'center',
  },
  uploadingContainer: {
    alignItems: 'center',
    paddingVertical: SIZES.padding,
  },
  uploadingText: {
    marginTop: SIZES.margin,
    color: COLORS.text,
    fontStyle: 'italic',
  },
  uploadButton: {
    backgroundColor: COLORS.success,
  },
  infoCard: {
    padding: SIZES.padding,
    borderRadius: SIZES.borderRadius,
    backgroundColor: COLORS.surface,
  },
  infoTitle: {
    fontSize: 18,
    color: COLORS.text,
    marginBottom: SIZES.padding,
  },
  infoList: {
    gap: SIZES.margin / 2,
  },
  infoItem: {
    color: COLORS.textLight,
    fontSize: 14,
  },
});
