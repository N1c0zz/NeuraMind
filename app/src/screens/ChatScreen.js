import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  StyleSheet,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';
import {
  TextInput,
  Button,
  Card,
  Text,
  IconButton,
  Surface,
  ActivityIndicator,
} from 'react-native-paper';
import { COLORS, SIZES, MESSAGES, CONFIG } from '../utils/constants';
import apiService from '../services/apiService';

export default function ChatScreen() {
  const [messages, setMessages] = useState([
    {
      id: '1',
      text: 'Ciao! Sono il tuo assistente AI. Puoi farmi domande sui documenti che hai caricato.',
      isUser: false,
      timestamp: new Date(),
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const flatListRef = useRef(null);

  useEffect(() => {
    // Scorri verso il basso quando arrivano nuovi messaggi
    if (messages.length > 0) {
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [messages]);

  const sendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      text: inputText.trim(),
      isUser: true,
      timestamp: new Date(),
    };

    // Aggiungi messaggio utente
    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    // Aggiungi messaggio "typing"
    const typingMessage = {
      id: 'typing',
      text: MESSAGES.query.thinking,
      isUser: false,
      timestamp: new Date(),
      isTyping: true,
    };
    setMessages(prev => [...prev, typingMessage]);

    try {
      // Chiama l'API per ottenere la risposta
      const response = await apiService.askQuestion(CONFIG.USER_ID, userMessage.text);
      
      // Rimuovi messaggio typing
      setMessages(prev => prev.filter(msg => msg.id !== 'typing'));
      
      // Aggiungi risposta AI
      const aiMessage = {
        id: (Date.now() + 1).toString(),
        text: response.answer,
        isUser: false,
        timestamp: new Date(),
        sources: response.sources,
      };
      
      setMessages(prev => [...prev, aiMessage]);
      
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Rimuovi messaggio typing
      setMessages(prev => prev.filter(msg => msg.id !== 'typing'));
      
      // Aggiungi messaggio di errore
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        text: 'Mi dispiace, si è verificato un errore. Assicurati di aver caricato alcuni documenti e riprova.',
        isUser: false,
        timestamp: new Date(),
        isError: true,
      };
      
      setMessages(prev => [...prev, errorMessage]);
      
      Alert.alert(
        'Errore',
        'Non sono riuscito a elaborare la tua richiesta. Verifica la connessione e riprova.',
        [{ text: 'OK' }]
      );
    } finally {
      setIsLoading(false);
    }
  };

  const showSources = (sources) => {
    if (!sources || sources.length === 0) return;
    
    const sourceTexts = sources.map((source, index) => 
      `${index + 1}. ${source.metadata.title || 'Documento'}\nSimilarità: ${(source.score * 100).toFixed(1)}%`
    ).join('\n\n');
    
    Alert.alert(
      'Fonti utilizzate',
      sourceTexts,
      [{ text: 'Chiudi' }]
    );
  };

  const renderMessage = ({ item }) => {
    const isUser = item.isUser;
    
    return (
      <View style={[
        styles.messageContainer,
        isUser ? styles.userMessageContainer : styles.aiMessageContainer
      ]}>
        <Surface
          style={[
            styles.messageCard,
            isUser ? styles.userMessage : styles.aiMessage,
            item.isError && styles.errorMessage,
          ]}
          elevation={isUser ? 2 : 1}
        >
          {item.isTyping ? (
            <View style={styles.typingContainer}>
              <ActivityIndicator size="small" color={COLORS.primary} />
              <Text style={styles.typingText}>{item.text}</Text>
            </View>
          ) : (
            <>
              <Text style={[
                styles.messageText,
                isUser ? styles.userMessageText : styles.aiMessageText,
                item.isError && styles.errorMessageText,
              ]}>
                {item.text}
              </Text>
              
              {/* Timestamp */}
              <Text style={[
                styles.timestamp,
                isUser ? styles.userTimestamp : styles.aiTimestamp
              ]}>
                {item.timestamp.toLocaleTimeString('it-IT', { 
                  hour: '2-digit', 
                  minute: '2-digit' 
                })}
              </Text>
              
              {/* Pulsante fonti per messaggi AI con fonti */}
              {!isUser && item.sources && item.sources.length > 0 && (
                <Button
                  mode="text"
                  onPress={() => showSources(item.sources)}
                  style={styles.sourcesButton}
                  labelStyle={styles.sourcesButtonText}
                >
                  Mostra fonti ({item.sources.length})
                </Button>
              )}
            </>
          )}
        </Surface>
      </View>
    );
  };

  const quickQuestions = [
    "Riassumi i documenti caricati",
    "Cosa contengono i miei documenti?",
    "Cerca informazioni specifiche",
  ];

  const sendQuickQuestion = (question) => {
    setInputText(question);
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
    >
      {/* Lista messaggi */}
      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={renderMessage}
        keyExtractor={item => item.id}
        style={styles.messagesList}
        contentContainerStyle={styles.messagesContent}
        showsVerticalScrollIndicator={false}
      />
      
      {/* Domande rapide (solo se nessun messaggio dell'utente) */}
      {messages.length === 1 && (
        <View style={styles.quickQuestionsContainer}>
          <Text style={styles.quickQuestionsTitle}>Domande suggerite:</Text>
          {quickQuestions.map((question, index) => (
            <Button
              key={index}
              mode="outlined"
              onPress={() => sendQuickQuestion(question)}
              style={styles.quickQuestionButton}
              labelStyle={styles.quickQuestionText}
            >
              {question}
            </Button>
          ))}
        </View>
      )}
      
      {/* Input area */}
      <Surface style={styles.inputContainer} elevation={4}>
        <View style={styles.inputRow}>
          <TextInput
            style={styles.textInput}
            value={inputText}
            onChangeText={setInputText}
            placeholder="Scrivi la tua domanda..."
            multiline
            maxLength={500}
            mode="outlined"
            disabled={isLoading}
            onSubmitEditing={sendMessage}
            blurOnSubmit={false}
          />
          <IconButton
            icon="send"
            size={24}
            iconColor={inputText.trim() && !isLoading ? COLORS.blue : COLORS.textLight}
            disabled={!inputText.trim() || isLoading}
            onPress={sendMessage}
            style={styles.sendButton}
          />
        </View>
      </Surface>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  messagesList: {
    flex: 1,
  },
  messagesContent: {
    padding: SIZES.padding,
    paddingBottom: SIZES.padding * 2,
  },
  messageContainer: {
    marginBottom: SIZES.margin,
  },
  userMessageContainer: {
    alignItems: 'flex-end',
  },
  aiMessageContainer: {
    alignItems: 'flex-start',
  },
  messageCard: {
    maxWidth: '80%',
    borderRadius: SIZES.borderRadius,
    padding: SIZES.padding,
  },
  userMessage: {
    backgroundColor: COLORS.blue,
  },
  aiMessage: {
    backgroundColor: COLORS.surface,
  },
  errorMessage: {
    backgroundColor: COLORS.error,
  },
  messageText: {
    fontSize: 16,
    lineHeight: 22,
  },
  userMessageText: {
    color: 'white',
  },
  aiMessageText: {
    color: COLORS.text,
  },
  errorMessageText: {
    color: 'white',
  },
  timestamp: {
    fontSize: 12,
    marginTop: SIZES.margin / 2,
  },
  userTimestamp: {
    color: 'rgba(255, 255, 255, 0.7)',
    textAlign: 'right',
  },
  aiTimestamp: {
    color: COLORS.textLight,
  },
  typingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  typingText: {
    marginLeft: SIZES.margin,
    color: COLORS.text,
    fontStyle: 'italic',
  },
  sourcesButton: {
    marginTop: SIZES.margin / 2,
    alignSelf: 'flex-start',
  },
  sourcesButtonText: {
    fontSize: 12,
    color: COLORS.blue,
  },
  quickQuestionsContainer: {
    padding: SIZES.padding,
    backgroundColor: COLORS.surface,
    borderTopWidth: 1,
    borderTopColor: COLORS.background,
  },
  quickQuestionsTitle: {
    fontSize: 14,
    color: COLORS.textLight,
    marginBottom: SIZES.margin,
  },
  quickQuestionButton: {
    marginBottom: SIZES.margin / 2,
  },
  quickQuestionText: {
    fontSize: 14,
  },
  inputContainer: {
    backgroundColor: COLORS.surface,
    borderTopWidth: 1,
    borderTopColor: COLORS.background,
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    padding: SIZES.padding,
  },
  textInput: {
    flex: 1,
    maxHeight: 120,
    backgroundColor: COLORS.background,
  },
  sendButton: {
    marginLeft: SIZES.margin / 2,
  },
});
