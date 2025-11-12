import React, { useEffect, useState, useRef } from "react";
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  Dimensions,
  Image,
  Platform,
} from "react-native";
// constants removed
import Header from "../components/Header";

export default function Home({ navigation }) {
  const { height: windowHeight } = Dimensions.get("window");
  const topOffset = Math.round(windowHeight * 0.08);
  const STREAM_URL = 'http://172.23.180.66/stream';
  const [ts, setTs] = useState(Date.now());
  const [loading, setLoading] = useState(true);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    intervalRef.current = setInterval(() => setTs(Date.now()), 800);
    return () => clearInterval(intervalRef.current);
  }, []);

  const uri = STREAM_URL;

  return (
    <View style={[styles.container, { paddingTop: topOffset }]}> 
      <Header navigation={navigation} currentScreen="Home" />

      <Text style={styles.screenTitle}>Live View</Text>

    <Text style={styles.statusText}>{loading ? 'Connecting to device...' : `Streaming: ${STREAM_URL}`}</Text>

      <View style={styles.controlsRow} />

      <View style={styles.videoContainer}>
        <View style={styles.videoPlaceholder}>
          <Image
            source={{ uri }}
            style={styles.streamImage}
            onLoad={() => setLoading(false)}
            onError={() => setLoading(true)}
            resizeMode="cover"
          />
          {loading && (
            <View style={styles.overlayCenter} pointerEvents="none">
              <ActivityIndicator size="large" color="#666" />
              <Text style={styles.connectingText}>Connecting to device...</Text>
            </View>
          )}
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#000" },
  screenTitle: { color: "#fff", fontSize: 30, textAlign: "center", marginTop: 18, marginBottom: 18, fontWeight: "600" },
  videoContainer: { alignItems: "center", paddingHorizontal: 16 },
  videoPlaceholder: {
    width: "95%",
    aspectRatio: 1,
    backgroundColor: "#e6e6e6",
    alignItems: "center",
    justifyContent: "center",
    borderRadius: 12,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.12,
    shadowRadius: 10,
    elevation: 6,
  },
  streamImage: { width: "100%", height: "100%", borderRadius: 12 },
  overlayCenter: { position: "absolute", alignItems: "center", justifyContent: "center" },
  controlsRow: { flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 8, marginBottom: 12 },
  hostInput: { backgroundColor: "#222", color: "#fff", paddingHorizontal: 12, paddingVertical: 8, borderRadius: 8, minWidth: 140, marginRight: 8 },
  portInput: { backgroundColor: "#222", color: "#fff", paddingHorizontal: 12, paddingVertical: 8, borderRadius: 8, width: 80, marginRight: 8 },
  connectButton: { backgroundColor: "#4a90e2", paddingHorizontal: 12, paddingVertical: 10, borderRadius: 8 },
  connectText: { color: "#fff", fontWeight: "600" },
  connectingText: { color: "#666", marginTop: 12, fontSize: 18 },
});
