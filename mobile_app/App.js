import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
  StyleSheet,
  Platform
} from 'react-native';

const API_BASE_URL = 'http://your-server-ip:5000/api';

export default function App() {
  const [patientData, setPatientData] = useState({
    firstName: '',
    lastName: '',
    gender: 'unknown',
    birthDate: '',
    phone: '',
    email: '',
    address: '',
    city: '',
    state: '',
    postalCode: '',
    condition: ''
  });

  const [loading, setLoading] = useState(false);

  const createPatient = async () => {
    if (!patientData.firstName || !patientData.lastName) {
      Alert.alert('Error', 'First name and last name are required');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/patient`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(patientData),
      });

      const result = await response.json();
      
      if (result.success) {
        Alert.alert(
          'Success',
          `Patient created successfully!\nBundle ID: ${result.bundle_id}`,
          [
            { text: 'Download JSON', onPress: () => downloadBundle(result.bundle_id, 'json') },
            { text: 'Download CSV', onPress: () => downloadBundle(result.bundle_id, 'csv') },
            { text: 'OK' }
          ]
        );
      } else {
        Alert.alert('Error', result.error);
      }
    } catch (error) {
      Alert.alert('Error', 'Network error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadBundle = (bundleId, format) => {
    const url = `${API_BASE_URL}/${format === 'csv' ? `export/${bundleId}/csv` : `download/${bundleId}`}`;
    // In a real app, you'd use a library like react-native-fs to download files
    console.log('Download URL:', url);
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>FHIR Patient Entry</Text>
        <Text style={styles.subtitle}>Mobile Healthcare Data Entry</Text>
      </View>

      <View style={styles.form}>
        <TextInput
          style={styles.input}
          placeholder="First Name *"
          value={patientData.firstName}
          onChangeText={(text) => setPatientData({...patientData, firstName: text})}
        />
        
        <TextInput
          style={styles.input}
          placeholder="Last Name *"
          value={patientData.lastName}
          onChangeText={(text) => setPatientData({...patientData, lastName: text})}
        />

        <TextInput
          style={styles.input}
          placeholder="Phone"
          value={patientData.phone}
          onChangeText={(text) => setPatientData({...patientData, phone: text})}
          keyboardType="phone-pad"
        />

        <TextInput
          style={styles.input}
          placeholder="Email"
          value={patientData.email}
          onChangeText={(text) => setPatientData({...patientData, email: text})}
          keyboardType="email-address"
        />

        <TextInput
          style={styles.input}
          placeholder="Medical Condition"
          value={patientData.condition}
          onChangeText={(text) => setPatientData({...patientData, condition: text})}
        />

        <TouchableOpacity
          style={[styles.button, loading && styles.buttonDisabled]}
          onPress={createPatient}
          disabled={loading}
        >
          <Text style={styles.buttonText}>
            {loading ? 'Creating...' : 'Create Patient'}
          </Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#667eea',
    padding: 20,
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
  },
  subtitle: {
    fontSize: 16,
    color: 'white',
    marginTop: 5,
  },
  form: {
    padding: 20,
  },
  input: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 15,
    marginBottom: 15,
    fontSize: 16,
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
      },
      android: {
        elevation: 2,
      },
    }),
  },
  button: {
    backgroundColor: '#667eea',
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
    marginTop: 10,
  },
  buttonDisabled: {
    backgroundColor: '#ccc',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
