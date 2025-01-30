import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes
import pymysql

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection function
def create_connection():
    try:
        connection = pymysql.connect(
            host='127.0.0.1',
            user='root',
            database='donationprogramma',  # Replace with your actual database name
            port=3306,
            cursorclass=pymysql.cursors.DictCursor,
            ssl={'ssl': False}
        )
        return connection
    except pymysql.Error as e:
        logger.error(f"Error connecting to the database: {e}")
        return None

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Welcome! Use /info to see available commands.')

# Command handler for listing projects
async def list_projects(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    connection = create_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                query = "SELECT code_proetks, NameProekt, OpisanieProekta, SummaSbora FROM proekts"
                cursor.execute(query)
                projects = cursor.fetchall()

                if projects:
                    project_list = "\n\n".join([
                        f"Code: {proj['code_proetks']}\n"
                        f"Name: {proj['NameProekt']}\n"
                        f"Description: {proj['OpisanieProekta']}\n"
                        f"Collected: {proj['SummaSbora']}"
                        for proj in projects
                    ])
                    await update.message.reply_text(f"Projects:\n\n{project_list}")
                else:
                    await update.message.reply_text("No projects found.")
        except pymysql.MySQLError as e:
            logger.error(f"Database error: {e}")
            await update.message.reply_text("An error occurred while fetching projects.")
        finally:
            connection.close()
    else:
        await update.message.reply_text("Failed to connect to the database.")

# Command handler for providing information
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    info_message = (
        "To make a donation, enter the project code and amount separated by a space.\n"
        "To view projects, use /proekts."
    )
    await update.message.reply_text(info_message)

# Message handler for processing donations
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.strip()
    if text.startswith('/'):
        return  # Ignore commands

    try:
        project_code, amount_str = text.split()
        amount = float(amount_str)

        connection = create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    # Update the donation amount in the proekts table
                    update_query = "UPDATE proekts SET SummaSbora = SummaSbora + %s WHERE code_proetks = %s"
                    cursor.execute(update_query, (amount, project_code))
                    connection.commit()
                    await update.message.reply_text(f"Successfully added {amount} to project {project_code}.")
            except pymysql.MySQLError as e:
                logger.error(f"Database error: {e}")
                await update.message.reply_text("An error occurred while updating the database.")
            finally:
                connection.close()
        else:
            await update.message.reply_text("Failed to connect to the database.")
    except ValueError:
        await update.message.reply_text("Please send the project code and donation amount separated by a space.")
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("An unexpected error occurred.")

def main() -> None:
    # Create the Application and pass it your bot's token
    application = ApplicationBuilder().token("7930333013:AAFtMw_-P-bUYkNLZVpZeVvHMEEKUQb0_vQ").build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("proekts", list_projects))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(MessageHandler(None, handle_message))  # No filters used

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()