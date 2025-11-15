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
import Header from "../components/Header";

export default function Home({ navigation }) {
  const { height: windowHeight } = Dimensions.get("window");
  const topOffset = Math.round(windowHeight * 0.08);

  const STREAM_URL = "http://172.23.181.202:8080/frame";
  // HARDED CODED IP USED FOR TESTING PURPOSES JUST FOR NOW I WILL REMOVE IT LATER TRUST

  const [ts, setTs] = useState(Date.now());
  const [loading, setLoading] = useState(true);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    intervalRef.current = setInterval(() => setTs(Date.now()), 33); 
    return () => clearInterval(intervalRef.current);
  }, []);

  const uri = `${STREAM_URL}?_=${ts}`;

  return (
    <View style={[styles.container, { paddingTop: topOffset }]}>
      <Header navigation={navigation} currentScreen="Home" />

      <Text style={styles.screenTitle}>Live View</Text>

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

      {/* Activity Log Area */}
      <View style={styles.logBox}>
        <Text style={styles.logTitle}>Activity Log</Text>
        <Text style={styles.logText}>Awaiting events...</Text>
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
    backgroundColor: "#000",
    alignItems: "center",
    justifyContent: "center",
    borderRadius: 12,
    borderColor: "#fff",
    borderWidth: 2,
  },
  streamImage: { width: "100%", height: "100%", borderRadius: 12 },
  overlayCenter: { position: "absolute", alignItems: "center", justifyContent: "center" },
  connectingText: { color: "#fff", marginTop: 12, fontSize: 16 },

  logBox: {
    width: "90%",
    minHeight: 70,
    backgroundColor: "#111",
    borderRadius: 10,
    marginTop: 18,
    alignSelf: "center",
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderColor: "#fff",
    borderWidth: 2,
  },
  logTitle: {
    color: "#fff",
    fontSize: 18,
    fontWeight: "700",
    marginBottom: 4,
  },
  logText: {
    color: "#bbb",
    fontSize: 15,
    fontStyle: "italic",
  },
});
