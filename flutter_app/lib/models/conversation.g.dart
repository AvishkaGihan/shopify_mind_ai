// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'conversation.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class ConversationAdapter extends TypeAdapter<Conversation> {
  @override
  final int typeId = 0;

  @override
  Conversation read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return Conversation(
      id: fields[0] as String,
      userId: fields[1] as String,
      customerIdentifier: fields[2] as String?,
      customerMessage: fields[3] as String,
      aiResponse: fields[4] as String,
      messageCount: fields[5] as int,
      productsReferenced: (fields[6] as List).cast<String>(),
      intentDetected: fields[7] as String?,
      sentimentScore: fields[8] as double?,
      responseTimeMs: fields[9] as int?,
      createdAt: fields[10] as DateTime,
    );
  }

  @override
  void write(BinaryWriter writer, Conversation obj) {
    writer
      ..writeByte(11)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.userId)
      ..writeByte(2)
      ..write(obj.customerIdentifier)
      ..writeByte(3)
      ..write(obj.customerMessage)
      ..writeByte(4)
      ..write(obj.aiResponse)
      ..writeByte(5)
      ..write(obj.messageCount)
      ..writeByte(6)
      ..write(obj.productsReferenced)
      ..writeByte(7)
      ..write(obj.intentDetected)
      ..writeByte(8)
      ..write(obj.sentimentScore)
      ..writeByte(9)
      ..write(obj.responseTimeMs)
      ..writeByte(10)
      ..write(obj.createdAt);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ConversationAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}
